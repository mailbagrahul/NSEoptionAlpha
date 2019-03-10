# -*- coding: utf-8 -*-
# @Author: Popeye
# @Date:   2019-02-16 13:59:32
# @Last Modified by:   Raaghul Umapathy
# @Last Modified time: 2019-03-10 16:20:07

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html
import plotly.graph_objs as go

from flask import send_from_directory
from flask_caching import Cache
import flask

from datetime import datetime as dt
import pandas as pd
import json
import time
import os

# Local modules
import NSE_Options_Data as optdata
import get_expiry


# For including custom CSS
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # 'https://codepen.io/chriddyp/pen/brPBPO.css'
    'https://fonts.googleapis.com/icon?family=Material+Icons',
    "https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css",
    # "https://codepen.io/mailbagrahul/pen/jdVPzO.css"
    # 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'
]


# Initial Dash server
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.title = 'Options Analytics for NSE'


# Tabs style
card_style = {
    "box-shadow": "0 4px 5px 0 rgba(0,0,0,0.14), 0 1px 10px 0 rgba(0,0,0,0.12), 0 2px 4px -1px rgba(0,0,0,0.3)"
}


# setting up caching databse
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    # 'CACHE_THRESHOLD': 50  # should be equal to maximum number of active users
})


# Get Symbol list from NSE
symbols = pd.read_excel("Symbols_list.xlsx", sheet_name='Sheet1')

#

TIMEOUT = 60


@cache.memoize(timeout=TIMEOUT)
def get_option_data(symbolname, e_date):

    print("processing new data")
    if isinstance(e_date, dict):
        exp_date = e_date['value']
    else:
        exp_date = e_date

    search_string = "&symbol=" + symbolname + "&date=" + exp_date
    Scrp_option_data = optdata.fetch_and_manipulate_data(search_string)
    return Scrp_option_data


def generate_option_data(symbolname, e_date):

    # Add logic in future for deserializing tuplue
    return get_option_data(symbolname, e_date)


app.config['suppress_callback_exceptions'] = True


app.layout = html.Div([

    html.Div(
        [
            html.P(children='NSE Option Analysis', style={'text-align': 'center', 'font-size': '5em'})
        ]
    ),

    html.Div(className="input-container", children=[
        html.Div(className="area1", children=[
            html.Label('Symbol'),
            dcc.Dropdown(
                id="symbol",
                options=[
                    {'label': symb, 'value': symb} for symb in symbols['Symbol']],
                value=symbols['Symbol'][0]
            ),
        ], style={'width': '250px', 'margin-right': 'auto',
                  'margin-left': 'auto', 'text-align': 'center'}
        ),

        html.Div(className="area2", children=[
            html.Label('Expiry'),
            dcc.Loading(id="loading-1", children=[html.Div([dcc.Dropdown(id='dd_expirydate')]
                                                           )], type="dot")
        ], style={'width': '250px', 'margin-right': 'auto',
                  'margin-left': 'auto', 'text-align': 'center'}
        ),

        html.Div(className="area3", children=[
            html.Button(id='refresh-btn', n_clicks=0, children='Refresh')
            # [html.Img(src='/assets/refresh.png')]
        ], style={'width': '250px', 'margin-right': 'auto',
                  'margin-left': 'auto', 'text-align': 'center'}),
    ]),

    html.Hr(),

    html.Div([html.Span(id='price_id'),
              html.Span(id='pcr_id'),
              html.Span(id='maxpain_id')
              ], style={'display': 'inline-block'}
             ),


    # html.Hr(),
    html.Div([
        dcc.Tabs(id="tabs", value='oi_tab', children=[
            dcc.Tab(label='Open Interest', value='oi_tab'),
            dcc.Tab(label='Change in OI', value='oi_change_tab'),
            # dcc.Tab(label='Technical Chart', value='Chart_tab'),
        ], colors={
            "primary": "white",
            "background": "white",
            "border": "#d2d2d2",
        },
            parent_style=card_style,
        ),

        # html.Div(id='tabs-content', className='pv2')
        html.Div(
            children=[
                dcc.Loading(id='tabs-content',
                            type='graph', className='pv2')
            ]
        ),
    ]),
    html.Hr(),
    dcc.Markdown('Created by [Raaghul Umapathy](https://twitter.com/rahul_sailorman)'),

    # hidden signal value - Storing in intermediate data for accessing different callbacks
    html.Div(id='signal', style={'display': 'none'})


], className='container'
)

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


# Callback for storing option data to hidden DIV-signal
@app.callback(
    Output('signal', 'children'),
    [Input('symbol', 'value'),
     Input('dd_expirydate', 'value'),
     Input('refresh-btn', 'n_clicks')
     ])
def update_expiry_value(symbolname, e_date, n_clicks):

    if n_clicks is not None:
        # call expensive scrape call to store

        bulk_data_temp = generate_option_data(symbolname, e_date)

        bulk_data = {'symbol': symbolname, 'expiry_date': e_date, 'option_data': bulk_data_temp[0].to_json(orient='split'), 'underlying_spot_price': bulk_data_temp[1], 'Maxpain_Strike': bulk_data_temp[2], 'PCR_Value': bulk_data_temp[3]}

        return json.dumps(bulk_data)


# only for label text
output_elements = ['price_id', 'pcr_id', 'maxpain_id', 'tabs-content']


def create_callback(output_id):
    def callback(selected_tab, jsonified_cleaned_data):

        datasets = json.loads(jsonified_cleaned_data)

        if output_id == 'tabs-content':
            if selected_tab == 'oi_tab':
                Scrp_data_upd = pd.read_json(datasets['option_data'], orient='split')
                return html.Div(id='loading-1', children=[
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
                                'layout': go.Layout(
                            # title='Open Interest',
                            xaxis=dict(title="Strike Price",
                                       # tickangle=-90,
                                       showline=True,
                                       # tickmode="linear",
                                       # dtick=100,
                                       type="category"
                                       ),


                            yaxis=dict(title="Open Interest", autorange=True, showgrid=False,
                                       # gridwidth=4,
                                       tickmode="auto", zeroline=True,
                                       type="linear", showticklabels=True,
                                       # automargin=True,
                                       tickformat="s", nticks=0,
                                       ),

                            yaxis2=dict(
                                title='PCR',
                                overlaying='y',
                                side='right',
                                showgrid=True,
                                gridcolor='#1d1d21',
                                rangemode='tozero'
                            ),
                            paper_bgcolor='#000000',
                            plot_bgcolor='#000000',
                            hovermode="closest",
                            # margin=dict(pad=0, r=80, b=80, l=80, t=40),
                            legend=dict(y=-0.3, x=0.3, orientation="h"),
                            showlegend=True,
                            # height=400,
                            # width=1000,
                            # barmode='overlay'
                        )
                        }
                    )
                ])
            elif selected_tab == 'oi_change_tab':
                Scrp_data_upd = pd.read_json(datasets['option_data'], orient='split')
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
                                'layout': go.Layout(xaxis=dict(title="Strike Price",
                                                               tickangle=-90,
                                                               showline=True,
                                                               type="category"),


                                                    yaxis=dict(title="Open Interest", autorange=True, showgrid=False, gridwidth=0, tickmode="auto", zeroline=True, type="linear", showticklabels=True, automargin=True, tickformat="s", nticks=0,
                                                               ),
                                                    hovermode="closest",
                                                    margin=dict(
                                                        l=80,
                                                        r=50,
                                                        t=40
                                ),
                            # margin=dict(pad=0, r=80, b=80, l=80, t=40),
                            legend=dict(y=-0.3, x=0.3, orientation="h"),
                            showlegend=True,
                            height=400,
                            width=1000,
                            # barmode='overlay'
                        )
                        }
                    )
                ])
            # elif selected_tab == 'Chart_tab':
            #     return html.Div([
            #         dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
            #                 <iframe height="400" width="1500" src="https://ssltvc.forexprostools.com/?pair_ID=8985&height=400&width=1500&interval=86400&plotStyle=candles&domain_ID=1&lang_ID=1&timezone_ID=20"></iframe>
            #         '''),
            #     ])
        elif output_id == 'price_id':
            stock_price = datasets['underlying_spot_price']
            return '''
                {}
                '''.format(stock_price)
        elif output_id == 'pcr_id':
            PCR_Value = datasets['PCR_Value']
            return '''
                {}
                '''.format(PCR_Value)
        elif output_id == 'maxpain_id':
            Maxpain_Strike = datasets['Maxpain_Strike']
            return '''
                {}
                '''.format(Maxpain_Strike)

    return callback


for output_element in output_elements:
    dynamically_generated_function = create_callback(output_element)
    app.callback(Output(output_element, 'children'), [Input('tabs', 'value'),
                                                      Input('signal', 'children')])(dynamically_generated_function)


# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd() 'static')
#     return send_from_directory(static_folder, path)


if __name__ == '__main__':
    app.run_server()
    # app.run_server(debug=True, port="10582")  # for development....
