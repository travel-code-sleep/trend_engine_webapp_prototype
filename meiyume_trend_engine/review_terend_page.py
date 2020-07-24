""" [summary]

[extended_summary]
"""
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from path import Path
import json
import re

three_yrs_ago = dt.now() - relativedelta(years=3)

default_start_date = str(pd.to_datetime(
    three_yrs_ago.strftime('%m/%d/%Y')))[:10].split('-')
default_start_date[-1] = '01'
default_start_date = ('-').join(default_start_date)

default_end_date = str(pd.to_datetime(
    dt.today().strftime('%m/%d/%Y')))[:10].split('-')
default_end_date[-1] = '01'
default_end_date = ('-').join(default_end_date)


dash_data_path = Path(r'D:\Amit\Meiyume\meiyume_data\dash_data')

app = dash.Dash()

category_trend_df = pd.read_feather(
    dash_data_path/'review_trend_category_month')
product_type_trend_df = pd.read_feather(
    dash_data_path/'review_trend_product_type_month')

category_options = [{'label': i, 'value': i}
                    for i in category_trend_df.category.unique()]
source_options = [{'label': i, 'value': i}
                  for i in category_trend_df.source.unique()]


def create_category_trend_figure(data, source='us',
                                 category=category_trend_df.category.unique().tolist(),
                                 start_date=default_start_date, end_date=default_end_date):
    data = data[(data.month >= start_date) &
                (data.month <= end_date)]

    fig = px.area(data[(data.source == 'us') & (data.category.isin(category))],
                  x='month', y='review_text', facet_col='category',
                  facet_col_wrap=3, color='category',
                  hover_data=['category'],
                  title='Beauty Industry Category wise Review Trend')

    for axis in fig.layout:
        if type(fig.layout[axis]) == go.layout.YAxis:
            fig.layout[axis].title.text = ''
        if type(fig.layout[axis]) == go.layout.XAxis:
            fig.layout[axis].title.text = ''

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        annotations=list(fig.layout.annotations) +
        [go.layout.Annotation(
            x=-0.07,
            y=0.5,
            font=dict(
                size=14
            ),
            showarrow=False,
            text="Review Count",
            textangle=-90,
            xref="paper",
            yref="paper"
        )
        ],
        font_family="Gotham",
        font_color="blue",
        title_font_family="Gotham",
        title_font_color="blue",
        legend_title_font_color="green",
        hovermode='closest'
    )
    return fig


def create_product_type_trend_figure(data, source='us',
                                     category='bath-body', height=1000,
                                     start_date=default_start_date,
                                     end_date=default_end_date):
    data = data[(data.month >= start_date) &
                (data.month <= end_date)]
    fig = px.area(data[(data.category == category) &
                       (data.source == source)],
                  x='month', y='review_text', facet_col='product_type',
                  color='product_type', facet_col_wrap=5, height=height,
                  facet_row_spacing=0.04, facet_col_spacing=0.04,
                  title='Beauty Industry SubCategory wise Review Trend'
                  )

    for axis in fig.layout:
        if type(fig.layout[axis]) == go.layout.YAxis:
            fig.layout[axis].title.text = ''
        if type(fig.layout[axis]) == go.layout.XAxis:
            fig.layout[axis].title.text = ''

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        annotations=list(fig.layout.annotations) +
        [go.layout.Annotation(
            x=-0.07,
            y=0.5,
            font=dict(
                size=14
            ),
            showarrow=False,
            text="Review Count",
            textangle=-90,
            xref="paper",
            yref="paper"
        )
        ],
        font_family="Gotham",
        font_color="blue",
        title_font_family="Gotham",
        title_font_color="blue",
        legend_title_font_color="green",
        hovermode='closest'
    )
    return fig


category_trend_figure = create_category_trend_figure(category_trend_df)
subcategory_trend_figure = create_product_type_trend_figure(
    product_type_trend_df)


def layout():
    return html.Div(
        [
            html.H1('Beauty Trend Engine'),
            dcc.Tabs(
                [
                    dcc.Tab(label='Review_Trend',
                            children=[
                                html.Div(
                                    [
                                        html.H2('Review Trend',
                                                style={'paddingRight': '30px'}
                                                ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.H3('Select Geography',
                                                                style={
                                                                    'paddingRight': '30px'}
                                                                ),
                                                        dcc.Dropdown(id='source',
                                                                     options=source_options,
                                                                     multi=False,
                                                                     value='us',
                                                                     style={'fontSize': 14,
                                                                            'width': '50%'},
                                                                     placeholder='Select Geography'),
                                                    ],
                                                    style={'display': 'inline-block',
                                                           'verticalAlign': 'top',
                                                           'width': '25%'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.H3('Select Date Range',
                                                                style={
                                                                    'paddingRight': '20px'}
                                                                ),
                                                        dcc.DatePickerRange(id='review_month_range',
                                                                            min_date_allowed=dt(
                                                                                2008, 12, 1),
                                                                            max_date_allowed=dt.today()
                                                                            ),
                                                        html.Div(
                                                            id='output-container-date-picker-range')
                                                    ],
                                                    style={'display': 'inline-block',
                                                           'verticalAlign': 'top',
                                                           'width': '25%'}
                                                ),
                                                html.Div(
                                                    [
                                                        html.H3('Select Category',
                                                                style={
                                                                    'paddingRight': '30px'}
                                                                ),
                                                        dcc.Dropdown(id='category',
                                                                     options=category_options,
                                                                     multi=True,
                                                                     value=category_trend_df.category.unique().tolist(),
                                                                     style={'fontSize': 14,
                                                                            'width': '100%'},
                                                                     placeholder='Select Category')
                                                    ],
                                                    style={'display': 'inline-block',
                                                           'verticalAlign': 'top',
                                                           'width': '50%'}
                                                )
                                            ],
                                            style={'display': 'inline-block',
                                                   'verticalAlign': 'top',
                                                   'width': '100%'}
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(id='category_trend',
                                                          figure=category_trend_figure),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.H3('Review Subcategory Trend',
                                                        style={
                                                            'paddingRight': '30px'}
                                                        ),
                                                html.Div(id='category_name',
                                                         style={'fontSize': 24,
                                                                'fontFamily': "Gotham"
                                                                }),
                                                html.Hr(),
                                                dcc.Graph(id='subcategory_trend',
                                                          figure=subcategory_trend_figure)
                                            ]
                                        )
                                    ]
                                )

                            ]
                            ),
                    dcc.Tab(label='Tab two',
                            children=[
                                html.Div('Work in Progress')
                            ]
                            ),
                    dcc.Tab(label='Tab three',
                            children=[
                                html.Div('Work in Progress')
                            ]
                            ),
                ]
            )
        ]
    )


app.layout = layout()


@app.callback(Output('category_trend', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_trend_graph(source, category, start_date, end_date):

    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
    else:
        end_date_string = default_end_date

    fig = create_category_trend_figure(
        category_trend_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('category_name', 'children'),
              [Input('category_trend', 'clickData'),
               ])
def display_click_data(clickData):
    if clickData is not None:
        return clickData['points'][0]['customdata'][0]
    else:
        return ('bath-body')


@app.callback(Output('subcategory_trend', 'figure'),
              [Input('source', 'value'),
               Input('category_trend', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_subcategory_trend_graph(source, clickData, start_date, end_date):

    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
    else:
        end_date_string = default_end_date

    if clickData is not None:
        category = clickData['points'][0]['customdata'][0]
    else:
        category = 'bath-body'
    # pt_df = product_type_trend_df[(product_type_trend_df.category==category)
    #                               product_type_trend_df.source==source]
    product_type_count = len(product_type_trend_df[product_type_trend_df.category ==
                                                   category].product_type.unique())
    if product_type_count <= 10:
        height = 600
    elif product_type_count <= 20:
        height = 1200
    elif product_type_count <= 30:
        height = 1800
    elif product_type_count <= 50:
        height = 2200
    else:
        height = 2600

    fig = create_product_type_trend_figure(
        data=product_type_trend_df, source=source, category=category, height=height,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('review_month_range', 'start_date'),
     dash.dependencies.Input('review_month_range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '

    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
    else:
        start_date_string = default_start_date
    string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '

    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
    else:
        end_date_string = default_end_date

    string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == "__main__":
    app.run_server()
