import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import os
from flask import send_from_directory
# from server import server

import NSE_Options_Data as optdata

search_string = "segmentLink=17&instrument=OPTIDX&symbol=BANKNIFTY&date=27DEC2018"
Scrp_data_upd = optdata.fetch_and_manipulate_data(search_string)


external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # 'https://codepen.io/chriddyp/pen/brPBPO.css'

]
# url_base_pathname = '/ngrtzo/'

app = dash.Dash(name='nsealpha')

app.config.supress_callback_exceptions = True

for css in external_css:
    app.css.append_css({"external_url": css})

app.layout = html.Div([

    html.Div(
        [
            html.H3(children='Open Interest',
                    className='twelve columns'
                    )
        ], className="row"
    ),



    html.Div([dcc.Graph(id='oi_chart',
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
                                'layout': go.Layout(title='OI Analysis',
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
                                                    legend=dict(y=-0.2, x=0.5, orientation="h"),
                                                    showlegend=True,
                                                    height=500,
                                                    width=1500,
                                                    # barmode='overlay'
                                                    )
                                }

                        )])
])


# @app.callback(
#     Output('oi_chart', 'figure'),
#     [Input('button1', 'n_clicks')]
# )
# def update_chart(n_clicks, lob, effdate, activity, iteration, brand, state):

#     # return generate_table(Scrp_data_upd)
#     return {'data': [go.Bar(x=Scrp_data_upd['Bucket_Pct'],
#                             y=Scrp_data_upd['Policy_Count'],
#                             name='Policy Count'
#                             ),
#                      go.Scatter(x=Scrp_data_upd['Bucket_Pct'],
#                                 y=Scrp_data_upd['Distribution'],
#                                 mode='lines+markers',
#                                 name='Dist Percentage',
#                                 yaxis='y2'
#                                 )
#                      ],
#             'layout': go.Layout(title='Final_Premium_Distribution',
#                                 yaxis=dict(
#                                     title='Policy Count'
#                                 ),
#                                 yaxis2=dict(
#                                     title='Dist Percentage',
#                                     titlefont=dict(
#                                         color='rgb(148, 103, 189)'
#                                     ),
#                                     tickfont=dict(
#                                         color='rgb(148, 103, 189)'
#                                     ),
#                                     overlaying='y',
#                                     side='right'
#                                 )
#                                 )
#             }


# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd(), 'static')
#     return send_from_directory(static_folder, path)


if __name__ == '__main__':
    app.run_server(debug=True)
