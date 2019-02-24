# -*- coding: utf-8 -*-
# @Author: Popeye
# @Date:   2019-02-16 13:59:32
# @Last Modified by:   Raaghul Umapathy
# @Last Modified time: 2019-02-18 11:41:06

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html

import plotly.graph_objs as go

from flask import send_from_directory
from flask_caching import Cache

from datetime import datetime as dt
import pandas as pd
import os

# Local modules
import NSE_Options_Data as optdata
import get_expiry


# Initial Dash server
app = dash.Dash(name='nsealpha')


# For including custom CSS
external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # 'https://codepen.io/chriddyp/pen/brPBPO.css'
]


# setting up caching databse
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})


# Get Symbol list from NSE
symbols = pd.read_excel("Symbols_list.xlsx", sheet_name='Sheet1')

#

TIMEOUT = 60


@cache.memoize(timeout=TIMEOUT)
def get_option_data(symbolname, e_date):

    if isinstance(e_date, dict):
        exp_date = e_date['value']
    else:
        exp_date = e_date

    search_string = "&symbol=" + symbolname + "&date=" + exp_date
    Scrp_option_data = optdata.fetch_and_manipulate_data(search_string)
    return Scrp_option_data


app.config['suppress_callback_exceptions'] = True

# Adding custom CSS
for css in external_css:
    app.css.append_css({"external_url": css})


app.layout = html.Div([

    html.Div(
        [
            html.H1(children='Option Analysis')
        ]
    ),
    html.Div([
        html.Div([
            html.Label('Symbol'),
            dcc.Dropdown(
                id="symbol",
                options=[
                    {'label': symb, 'value': symb} for symb in symbols['Symbol']],
                value=symbols['Symbol'][0]
            ),
        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Expiry'),
            html.Div([dcc.Dropdown(id='dd_expirydate')])

        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Button(id='submit-button', n_clicks=0, children='Refresh')
        ], style={'width': '20%', 'float': 'right', 'display': 'inline-block'}),
    ]),
    html.Hr(),

    html.Div([html.Span(id='price_id'),
              html.Span(id='pcr_id'),
              html.Span(id='maxpain_id')
              ], style={'display': 'inline-block'}
             ),


    html.Hr(),
    html.Div([
        dcc.Tabs(id="tabs-example", value='oi_tab', children=[
            dcc.Tab(label='Open Interest', value='oi_tab'),
            dcc.Tab(label='Change in OI', value='oi_change_tab'),
            dcc.Tab(label='Technical Chart', value='Chart_tab'),
        ]),
        html.Div(id='tabs-content-example')
    ])
])

# Callback for expirty dates dropdown option


@app.callback(
    Output('dd_expirydate', 'options'),
    [Input('symbol', 'value')])
def update_expiry_options(symbolname):

    print(symbolname)
    expirydates = get_expiry.get_expiry_from_option_chain(symbolname)
    print(expirydates)
    return [{'label': exp_date, 'value': exp_date} for exp_date in expirydates]


# Callback for expirty dates dropdown value
@app.callback(
    Output('dd_expirydate', 'value'),
    [Input('dd_expirydate', 'options')])
def update_expiry_value(exp_options):

    return exp_options[0]


# only for label text
output_elements = ['price_id', 'pcr_id', 'maxpain_id', 'tabs-content-example']


def create_callback(output_id):
    def callback(e_date, symbolname, selected_tab, n_clicks):

        if output_id == 'tabs-content-example':
            if selected_tab == 'oi_tab':
                Scrp_data_upd = get_option_data(symbolname, e_date)[0]
                return html.Div([
                    # html.H3('Open Interest'),
                    dcc.Graph(
                        id='total_oi_graph',
                        figure={'data': [go.Bar(x=Scrp_data_upd['Strike_Price'],
                                                y=Scrp_data_upd['CALLS_OI'],
                                                name='Call Option OI',
                                                marker={'color': '#EC4849'},

                                                # width=1.5
                                                ),

                                         go.Bar(x=Scrp_data_upd['Strike_Price'],
                                                y=Scrp_data_upd['PUTS_OI'],
                                                name='Put Option OI',
                                                marker={'color': '#26ae60'},

                                                # width=1.5
                                                ),
                                         go.Scatter(x=Scrp_data_upd['Strike_Price'],
                                                    y=Scrp_data_upd['PCR_Strike'],
                                                    mode='lines+markers',
                                                    name='PCR',
                                                    marker={'color': '#EEC213'},
                                                    yaxis='y2',

                                                    )

                                         ],
                                'layout': go.Layout(title='Open Interest',
                                                    xaxis=dict(title="Strike Price",
                                                               tickangle=-90,
                                                               showline=True,
                                                               type="category"),


                                                    yaxis=dict(tickformat="0f", title="Open Interest", dtick=100000, showgrid=True, showline=True, type="linear",
                                                               ),


                                                    yaxis2=dict(
                                                        title='PCR',
                                                        # dtick=0,
                                                        overlaying='y',
                                                        side='right',
                                                        showgrid=False,
                                                        # tickmode='category',
                                                        # range=[0, 10.1], fixedrange=True
                                                    ),
                                                    hovermode="closest",
                                                    margin=dict(pad=0, r=80, b=80, l=80, t=40),
                                                    legend=dict(y=-0.2, x=0.3, orientation="h"),
                                                    showlegend=True,
                                                    height=500,
                                                    width=1500,
                                                    # barmode='overlay'
                                                    )
                                }
                    )
                ])
            elif selected_tab == 'oi_change_tab':
                Scrp_data_upd = get_option_data(symbolname, e_date)[0]
                return html.Div([
                    # html.H3('Change in OI'),
                    dcc.Graph(
                        id='oi_change_graph',
                        figure={'data': [go.Bar(x=Scrp_data_upd['Strike_Price'],
                                                y=Scrp_data_upd['CALLS_Chng_in_OI'],
                                                name='Call Option OI',
                                                marker={'color': '#EC4849'},

                                                # width=1.5
                                                ),

                                         go.Bar(x=Scrp_data_upd['Strike_Price'],
                                                y=Scrp_data_upd['PUTS_Chng_in_OI'],
                                                name='Put Option OI',
                                                marker={'color': '#26ae60'},

                                                # width=1.5
                                                )],
                                'layout': go.Layout(title='Change in OI',
                                                    xaxis=dict(title="Strike Price",
                                                               tickangle=-90,
                                                               showline=True,
                                                               type="category"),


                                                    yaxis=dict(tickformat="0f", title="Open Interest", dtick=100000, showgrid=True, showline=True, type="linear",
                                                               ),
                                                    hovermode="closest",
                                                    margin=dict(pad=0, r=80, b=80, l=80, t=40),
                                                    legend=dict(y=-0.2, x=0.3, orientation="h"),
                                                    showlegend=True,
                                                    height=500,
                                                    width=1500,
                                                    # barmode='overlay'
                                                    )
                                }
                    )
                ])
            elif selected_tab == 'Chart_tab':
                return html.Div([
                    dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
                            <iframe height="400" width="1500" src="https://ssltvc.forexprostools.com/?pair_ID=8985&height=400&width=1500&interval=86400&plotStyle=candles&domain_ID=1&lang_ID=1&timezone_ID=20"></iframe>
                    '''),
                ])
        elif output_id == 'price_id':
            return '''
                {}
                '''.format(output_id)
        elif output_id == 'pcr_id':
            return '''
                {}
                '''.format(output_id)
        elif output_id == 'maxpain_id':
            return '''
                {}
                '''.format(output_id)

    return callback


for output_element in output_elements:
    dynamically_generated_function = create_callback(output_element)
    app.callback(Output(output_element, 'children'), [Input('dd_expirydate', 'value'),
                                                      Input('symbol', 'value'),
                                                      Input('tabs-example', 'value'),
                                                      Input('submit-button', 'n_clicks')])(dynamically_generated_function)


# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd(), 'static')
#     return send_from_directory(static_folder, path)


if __name__ == '__main__':
    app.run_server(debug=True)
