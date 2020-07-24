"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import dash
import dash_auth
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

USERNAME_PASSWORD_PAIRS = [
    ['user', 'pwd123'], ['meiyume', 'pwd123']
]


dash_data_path = Path(r'D:\Amit\Meiyume\meiyume_data\dash_data')

# app = dash.Dash()
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H1("Beauty Trend Engine", className="display-4",
                style={'fontSize': 60,
                       'color': 'white',
                       'backgroundColor': 'black',
                       'fontFamily': 'Gotham',
                       'fontWeight': 'bold',
                       'textShadow': '#fc0 1px 0 10px'}
                ),
        html.Hr(),
        html.P(
            "Turn unstructured data to structured insights using Natural Language Processing and Deep Learning.",
            className="lead",
            style={'fontSize': '24', 'case': 'block'}
        ),
        dbc.Nav(
            [
                dbc.NavLink("Market Trend Page",
                            href="/page-1", id="page-1-link"),
                dbc.NavLink("Product Page", href="/page-2", id="page-2-link"),
                dbc.NavLink("Review Page", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

'''
Read all the data from flat files.
'''
# review trend data
review_trend_category_df = pd.read_feather(
    dash_data_path/'review_trend_category_month')
review_trend_product_type_df = pd.read_feather(
    dash_data_path/'review_trend_product_type_month')

influenced_review_trend_category_df = pd.read_feather(
    dash_data_path/'review_trend_by_marketing_category_month')
influenced_review_trend_product_type_df = pd.read_feather(
    dash_data_path/'review_trend_by_marketing_product_type_month')
# product launches trend data
meta_product_launch_trend_category_df = pd.read_feather(
    dash_data_path/'meta_product_launch_trend_category_month')
meta_product_launch_trend_product_type_df = pd.read_feather(
    dash_data_path/'meta_product_launch_trend_product_type_month')

''' create dropdown options '''
category_options = [{'label': i, 'value': i}
                    for i in review_trend_category_df.category.unique()]
source_options = [{'label': i, 'value': i}
                  for i in review_trend_category_df.source.unique()]

'''
create graph figure functions
'''


def create_category_review_trend_figure(data, source='us',
                                        category=review_trend_category_df.category.unique().tolist(),
                                        start_date=default_start_date, end_date=default_end_date):
    data = data[(data.month >= start_date) &
                (data.month <= end_date)]

    fig = px.area(data[(data.source == 'us') & (data.category.isin(category))],
                  x='month', y='review_text', facet_col='category',
                  facet_col_wrap=3, color='category', height=500,
                  hover_data=['category'], facet_row_spacing=0.1, facet_col_spacing=0.04,
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
            x=-0.05,
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


def create_product_type_review_trend_figure(data, source='us',
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
            x=-0.05,
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


def create_category_product_launch_figure(data, source='us',
                                          category=meta_product_launch_trend_category_df.category.unique().tolist(),
                                          start_date=default_start_date, end_date=default_end_date):
    data = data[(data.meta_date >= start_date) &
                (data.meta_date <= end_date)]

    fig = px.line(data[(data.source == source) & (data.category.isin(category))],
                  x="meta_date", y="new_product_count", color='category', hover_data=['category'],
                  hover_name="category", line_shape="spline", title='Product Launch in Categories over Month',
                  width=650, height=600)

    fig.update_traces(connectgaps=True,
                      mode='markers+lines')

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="Gotham",
        font_color="blue",
        title_font_family="Gotham",
        title_font_color="blue",
        legend_title_font_color="green",
        hovermode='closest',
        xaxis={'title': 'Month'},
        yaxis={'title': 'New Product Count'}
    )

    return fig


def create_product_type_product_launch_figure(data, source='us',
                                              category='bath-body',
                                              start_date=default_start_date, end_date=default_end_date):
    data = data[(data.meta_date >= start_date) &
                (data.meta_date <= end_date)]

    fig = px.line(data[(data.source == source) & (data.category == category)],
                  x="meta_date", y="new_product_count", color='product_type', line_group='category',
                  hover_name="category", hover_data=["category", "product_type", 'new_product_count'],
                  line_shape="spline", title='Product Launch in Subcategories over Month',
                  width=850, height=600)

    fig.update_traces(connectgaps=True,
                      mode='markers+lines')

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="Gotham",
        font_color="blue",
        title_font_family="Gotham",
        title_font_color="blue",
        legend_title_font_color="green",
        hovermode='closest',
        xaxis={'title': 'Month'},
        yaxis={'title': 'New Product Count'}
    )

    return fig


''' create initial figures/graphs. '''
category_trend_figure = create_category_review_trend_figure(
    review_trend_category_df)
subcategory_trend_figure = create_product_type_review_trend_figure(
    review_trend_product_type_df)

influenced_category_trend_figure = create_category_review_trend_figure(
    influenced_review_trend_category_df)
influenced_subcategory_trend_figure = create_product_type_review_trend_figure(
    influenced_review_trend_product_type_df)

product_launch_trend_category_figure = create_category_product_launch_figure(
    meta_product_launch_trend_category_df)

product_launch_trend_subcategory_figure = create_product_type_product_launch_figure(
    meta_product_launch_trend_product_type_df)


def review_trend_layout():
    return html.Div(
        [
            html.H1('Market Trends by Categories and Product Launches',
                    style={'color': 'black',
                           'border': '0.5px grey dotted',
                           'width': '60%'}
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
                                         value=review_trend_category_df.category.unique().tolist(),
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
            dcc.Tabs(
                [
                    dcc.Tab(label='Review_Trend',
                            children=[
                                html.Div(
                                    [
                                        html.H2('Review Trend',
                                                style={'paddingRight': '30px'}
                                                ),
                                        html.Hr(),

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

                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                    dcc.Tab(label='Reviews_by_Marketing',
                            children=[
                                html.Div(
                                    [
                                        html.H2('Review Trend by Marketing Output',
                                                style={'paddingRight': '30px'}
                                                ),
                                        html.Hr(),

                                        html.Div(
                                            [
                                                dcc.Graph(id='influenced_category_trend',
                                                          figure=influenced_category_trend_figure),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.H3('Review Subcategory Trend by Marketing Output',
                                                        style={
                                                            'paddingRight': '30px'}
                                                        ),
                                                html.Div(id='influenced_category_name',
                                                         style={'fontSize': 24,
                                                                'fontFamily': "Gotham"
                                                                }),
                                                html.Hr(),
                                                dcc.Graph(id='influenced_subcategory_trend',
                                                          figure=influenced_subcategory_trend_figure)
                                            ]
                                        )
                                    ]
                                )
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                    dcc.Tab(label='Product_Launch_Trend',
                            children=[
                                html.H2('Product Launch Trends and Intensity by Category',
                                        style={'paddingRight': '30px'}
                                        ),
                                html.Hr(),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Graph(id='product_launch_trend_category',
                                                                  figure=product_launch_trend_category_figure,
                                                                  ),
                                                    ],
                                                    className="six columns"
                                                ),

                                                html.Div(
                                                    [
                                                        html.Div(id='product_trend_category_name',
                                                                 style={'fontSize': 24,
                                                                        'textAlign': 'center',
                                                                        'fontFamily': "Gotham",
                                                                        'verticalAlign': 'top'
                                                                        }
                                                                 ),
                                                        html.Div(dcc.Graph(id='product_launch_trend_subcategory',
                                                                           figure=product_launch_trend_subcategory_figure,
                                                                           )
                                                                 )
                                                    ],
                                                    className="six columns"
                                                ),
                                            ],
                                            className="row"
                                        ),
                                        html.Div(
                                            [
                                                'place holder div'
                                            ],
                                            className="row"
                                        )

                                    ],
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                ],
                style=tabs_styles,
                colors={
                    "border": "white",
                    "primary": "gold",
                    "background": "cornsilk"
                }
            )
        ],
        style={'fontFamily': 'Gotham'}
    )


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(Output('category_trend', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_review_trend_figure(source, category, start_date, end_date):

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

    fig = create_category_review_trend_figure(
        review_trend_category_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('influenced_category_trend', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_influenced_review_trend_figure(source, category, start_date, end_date):

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

    fig = create_category_review_trend_figure(
        influenced_review_trend_category_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('influenced_category_name', 'children'),
              [Input('influenced_category_trend', 'clickData'),
               ])
def influenced_display_click_data(clickData):
    if clickData is not None:
        return clickData['points'][0]['customdata'][0]
    else:
        return ('bath-body')


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
def update_product_type_review_trend_figure(source, clickData, start_date, end_date):

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
    # pt_df = review_trend_product_type_df[(review_trend_product_type_df.category==category)
    #                               review_trend_product_type_df.source==source]
    product_type_count = len(review_trend_product_type_df[review_trend_product_type_df.category ==
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

    fig = create_product_type_review_trend_figure(
        data=review_trend_product_type_df, source=source, category=category, height=height,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('influenced_subcategory_trend', 'figure'),
              [Input('source', 'value'),
               Input('influenced_category_trend', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_influenced_review_trend_figure(source, clickData, start_date, end_date):

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
    # pt_df = review_trend_product_type_df[(review_trend_product_type_df.category==category)
    #                               review_trend_product_type_df.source==source]
    product_type_count = len(influenced_review_trend_product_type_df[influenced_review_trend_product_type_df.category ==
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

    fig = create_product_type_review_trend_figure(
        data=influenced_review_trend_product_type_df, source=source, category=category, height=height,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('review_month_range', 'start_date'),
     dash.dependencies.Input('review_month_range', 'end_date')])
def update_output(start_date, end_date):
    return 'The minimum date you can select is 2008-12-01. \n You can write in the the date box to filter in YYYY-MM-DD format.'


@app.callback(Output('product_launch_trend_category', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_product_launch_figure(source, category, start_date, end_date):

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

    fig = create_category_product_launch_figure(
        meta_product_launch_trend_category_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('product_trend_category_name', 'children'),
              [Input('product_launch_trend_category', 'clickData'),
               ])
def display_click_data_product_trend(clickData):
    if clickData is not None:
        return clickData['points'][0]['customdata'][0]
    else:
        return ('bath-body')


@app.callback(Output('product_launch_trend_subcategory', 'figure'),
              [Input('source', 'value'),
               Input('product_launch_trend_category', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_product_launch_figure(source, clickData, start_date, end_date):

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

    fig = create_product_type_product_launch_figure(
        data=meta_product_launch_trend_product_type_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return review_trend_layout()  # html.P("This is the content of page 1!")
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server()
