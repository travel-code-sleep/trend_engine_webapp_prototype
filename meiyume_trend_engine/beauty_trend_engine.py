""" This app creates a sidebar layout using inline style arguments and the dbc.Nav component for Beauty Trend Engine.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.
"""
import json
import re
import base64
from datetime import datetime as dt

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State, ClientsideFunction
from dateutil.relativedelta import relativedelta
from path import Path

from bte_market_trend_page_data_and_plots import *

# assign default values
# px.defaults.template = "plotly_dark"

USERNAME_PASSWORD_PAIRS = [
    ['user', 'pwd123'], ['meiyume', 'pwd123']
]

# read and encode logo image
logo = 'assets/bte_logo.png'
logo_base64 = base64.b64encode(open(logo, 'rb').read()).decode('ascii')

# Create Dash Application
external_stylesheets = [dbc.themes.UNITED,
                        'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets,
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# create tab and sidebar css style sheets
tabs_styles = {'height': '44px'}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'}
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {"position": "fixed",
                 "top": 0,
                 "left": 0,
                 "bottom": 0,
                 "width": "18rem",
                 "padding": "2rem 1rem",
                 "background-color": "#f8f9fa"
                 }

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem", }

# create sidebar page layout and navigation
search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button("Search", color="primary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        dbc.Col(
            html.Div(
                [
                    html.H1("Beauty Trend Engine", className="display-4",
                            style={'fontSize': 50,
                                   'color': 'white',
                                   #    'backgroundColor': 'white',
                                   'fontFamily': 'Gotham',
                                   'fontWeight': 'bold',
                                   'textShadow': '#fc0 1px 0 10px'}
                            ),
                    # dbc.NavbarBrand("Navbar", className="ml-2"),
                ]
            ),
            width={'size': 5, 'offset': 2},
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
        dbc.Col(
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(
                        "More pages", header=True),
                    dbc.DropdownMenuItem(
                        "Market Trends", href="/page-2"),
                    dbc.DropdownMenuItem(
                        "Develop New Products", href="/page-3"),
                    dbc.DropdownMenuItem(
                        "Improve Existing Products", href="/page-4"),
                ],
                style={'fontSize': 24},
                in_navbar=True,
                label="Select Application",
            ),
            width={'size': 2},
        ),
    ],
    color="primary",
    dark=True,
)
# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
sidebar_header = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=f'data:image/png;base64,{logo_base64}', height='250px', width='200px'),
                        html.Hr(),
                        html.P(
                            "Turn unstructured data to structured insights using Natural Language Processing and Deep Learning.",
                            className="lead",
                            # style={'fontSize': '14', 'case': 'block'}
                        )
                    ]
                ),
                dbc.Col(
                    [
                        html.Button(
                            # use the Bootstrap navbar-toggler classes to style
                            className="navbar-toggler",
                            # the navbar-toggler classes don't set color,
                            id="sidebar-toggle",
                            style={"color": "orange",
                                   "border-color": "rgba(0,0,0,.1)",
                                   'background-color': 'orange',
                                   'width': '30px', 'height': '40px'
                                   }
                        ),
                    ],
                    # the column containing the toggle will be only as wide as the
                    # toggle, resulting in the toggle being right aligned
                    width={'size': "auto"},
                    # vertically align the toggle in the center
                ),
            ]
        )
    ],
)

sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink("Beauty Trend Engine Landing Page",
                                href="/page-1", id="page-1-link"),
                    dbc.NavLink("Market Trend Page",
                                href="/page-2", id="page-2-link"),
                    dbc.NavLink("Category Page", href="/page-3",
                                id="page-3-link"),
                    dbc.NavLink("Review Page", href="/page-4",
                                id="page-4-link"),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE
)
# sidebar = html.Div(
#     [html.Img(
#         src=f'data:image/png;base64,{logo_base64}', height='250px', width='200px'),
#         html.Hr(),
#         html.P(
#             "Turn unstructured data to structured insights using Natural Language Processing and Deep Learning.",
#             className="lead",
#             style={'fontSize': '24', 'case': 'block'}
#     ),
#         dbc.Nav(
#             [
#                 dbc.NavLink("Beauty Trend Engine Landing Page",
#                             href="/page-1", id="page-1-link"),
#                 dbc.NavLink("Market Trend Page",
#                             href="/page-2", id="page-2-link"),
#                 dbc.NavLink("Category Page", href="/page-3", id="page-3-link"),
#                 dbc.NavLink("Review Page", href="/page-4", id="page-4-link"),
#             ],
#             vertical=True,
#             pills=True,
#     ),
#     ],
#     style=SIDEBAR_STYLE,
# )

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.Row(
            dbc.Col(
                navbar,
                width={'size': 12}
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    sidebar,
                    content
                ]
            )
        ),
    ]
)


''' create dropdown options '''
category_options = [{'label': i, 'value': i}
                    for i in review_trend_category_df.category.unique()]
source_options = [{'label': i, 'value': i}
                  for i in review_trend_category_df.source.unique()]


def landing_page_layout():
    return html.Div(
        className='row',
        style={'verticalAlign': 'middle',
               'textAlign': 'center',
               'background-image': 'url(assets/landing_page_bg.jpg)',
               'width': '100%',
               'height': '100%',
               'top': '0px',
               'left': '0px'},
        children=[
            html.Div(
                [
                    html.P("Landing Page Work in Progress. Please click on Market Trend Page on the Sidebar to \
                            experience first complete page of Beauty Trend Engine. Yay!",
                           style={"background-color": "powderblue"})
                ]
            )
        ]
    )


def market_trend_page_layout():
    """market_trend_page_layout [summary]

    [extended_summary]

    Returns:
        html: market trend page layout
    """
    return html.Div(
        [
            html.H1('Market Trends by Categories and Product Launches',
                    style={'color': 'black',
                           'border': '0.5px grey dotted',
                           'width': '60%',
                           }
                    ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3('Select Geography',
                                    style={
                                        'paddingRight': '15px'}
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
                            dcc.Markdown(
                                id='output-container-date-picker-range',
                                style={'textAlign': 'left',
                                       'fontSize': '10'}
                            )
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
                                                dcc.Graph(id='product_launch_intensity_category',
                                                          figure=product_launch_intensity_category_figure,
                                                          ),
                                            ],
                                            className="row"
                                        )

                                    ],
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                    dcc.Tab(label='New_Ingredient_Trend',
                            children=[
                                html.H2('Ingredient Trends by Category',
                                        style={'paddingRight': '30px'}
                                        ),
                                html.Hr(),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Graph(id='ingredient_launch_trend_category',
                                                                  figure=new_ingredient_trend_category_figure,
                                                                  ),
                                                    ],
                                                    className="six columns"
                                                ),

                                                html.Div(
                                                    [
                                                        html.Div(id='ingredient_trend_category_name',
                                                                 style={'fontSize': 24,
                                                                        'textAlign': 'center',
                                                                        'fontFamily': "Gotham",
                                                                        'verticalAlign': 'top'
                                                                        }
                                                                 ),
                                                        html.Div(dcc.Graph(id='ingredient_launch_trend_subcategory',
                                                                              figure=new_ingredient_trend_product_type_figure,
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
                                                # dcc.Graph(id='ingredient_type_distribution',
                                                #           #   figure=product_launch_intensity_category_figure,
                                                #           ),
                                            ],
                                            className="row"
                                        )

                                    ],
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            )
                ],
                style=tabs_styles,
                colors={
                    "border": "white",
                    "primary": "gold",
                    "background": "cornsilk"
                }
            )
        ],
        style={'fontFamily': 'Gotham'},
        id="output-clientside"
    )


def category_product_performance_page_layout():
    return None


@app.callback(Output('category_trend', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_review_trend_figure(source: str, category: list, start_date: str, end_date: str)->go.Figure:
    """update_category_review_trend_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (list): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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
def update_category_influenced_review_trend_figure(source: str, category: list, start_date: str, end_date: str)->go.Figure:
    """update_category_influenced_review_trend_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (list): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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
def influenced_display_click_data(clickData)->str:
    """influenced_display_click_data [summary]

    [extended_summary]

    Args:
        clickData ([type]): [description]

    Returns:
        str: [description]
    """
    if clickData is not None:
        return f"Selected Category: {clickData['points'][0]['customdata'][0]}"
    else:
        return ('Selected Category: bath-body')


@app.callback(Output('category_name', 'children'),
              [Input('category_trend', 'clickData'),
               ])
def display_click_data(clickData)->str:
    """display_click_data [summary]

    [extended_summary]

    Args:
        clickData ([type]): [description]

    Returns:
        str: [description]
    """
    if clickData is not None:
        return f"Selected Category: {clickData['points'][0]['customdata'][0]}"
    else:
        return ('Selected Category: bath-body')


@app.callback(Output('subcategory_trend', 'figure'),
              [Input('source', 'value'),
               Input('category_trend', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_review_trend_figure(source: str, clickData, start_date: str, end_date: str)->go.Figure:
    """update_product_type_review_trend_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        clickData ([type]): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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
def update_product_type_influenced_review_trend_figure(source: str, clickData, start_date: str, end_date: str)->go.Figure:
    """update_product_type_influenced_review_trend_figure

    [extended_summary]

    Args:
        source (str): [description]
        clickData ([type]): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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
def date_selection_text(start_date: str, end_date: str)->str:
    """date_selection_text [summary]

    [extended_summary]

    Args:
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        str: [description]
    """
    return 'Minimum start date is 12/01/2008. \n You can write in MM/DD/YYYY format in the date box to filter.'


@app.callback(Output('product_launch_trend_category', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_product_launch_figure(source: str, category: list, start_date: str, end_date: str)->go.Figure:
    """update_category_product_launch_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (list): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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
def display_click_data_product_trend(clickData)->str:
    """display_click_data_product_trend [summary]

    [extended_summary]

    Args:
        clickData ([type]): [description]

    Returns:
        str: [description]
    """
    if clickData is not None:
        return f"Selected Category: {clickData['points'][0]['customdata'][0]}"
    else:
        ('Selected Category: bath-body')


@app.callback(Output('product_launch_trend_subcategory', 'figure'),
              [Input('source', 'value'),
               Input('product_launch_trend_category', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_product_launch_figure(source: str, clickData, start_date: str, end_date: str)->go.Figure:
    """update_product_type_product_launch_figure [summary]

    [extended_summary]

    Args:
        sourc (str): [description]
        clickData ([type]): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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


@app.callback(Output('product_launch_intensity_category', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_product_launch_intensity_figure(source: str, category: list, start_date: str, end_date: str)->go.Figure:
    """update_product_launch_intensity_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (list): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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

    fig = create_product_launch_intensity_figure(
        product_launch_intensity_category_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('ingredient_launch_trend_category', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_new_ingredient_trend_figure(source: str, category: list, start_date: str, end_date: str)->go.Figure:
    """update_category_new_ingredient_trend_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (list): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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

    fig = create_category_new_ingredient_trend_figure(
        new_ingredient_trend_category_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


@app.callback(Output('ingredient_trend_category_name', 'children'),
              [Input('ingredient_launch_trend_category', 'clickData'),
               ])
def display_click_data_product_trend(clickData)->str:
    """display_click_data_product_trend [summary]

    [extended_summary]

    Args:
        clickData ([type]): [description]

    Returns:
        str: [description]
    """
    if clickData is not None:
        return f"Selected Category: {clickData['points'][0]['customdata'][0]}"
    else:
        ('Selected Category: bath-body')


@app.callback(Output('ingredient_launch_trend_subcategory', 'figure'),
              [Input('source', 'value'),
               Input('ingredient_launch_trend_category', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_new_ingredient_trend_figure(source: str, clickData, start_date: str, end_date: str)->go.Figure:
    """update_product_type_new_ingredient_trend_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        clickData ([type]): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        go.Figure: [description]
    """

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

    fig = create_product_type_new_ingredient_trend_figure(
        data=new_ingredient_trend_product_type_df, source=source, category=category,
        start_date=start_date_string, end_date=end_date_string)
    return fig


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("yourGraph_ID", "figure")],
# )

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    if n and classname == "":
        return "collapsed"
    return ""


@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]


@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        # html.P("This is the content of page 1!")
        return landing_page_layout()
    elif pathname == "/page-2":
        return market_trend_page_layout()
    elif pathname == "/page-3":
        return html.P("This is the content of page 3. Yay!")
    elif pathname == "/page-4":
        return html.P("Oh cool, this is page 4!")
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
