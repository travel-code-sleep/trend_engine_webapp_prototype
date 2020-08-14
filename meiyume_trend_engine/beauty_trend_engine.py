""" This app creates a sidebar layout using inline style arguments and the dbc.Nav component for Beauty Trend Engine.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.
"""
import base64
import json
import re
from datetime import datetime as dt
from typing import Optional, Tuple, Union

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import ClientsideFunction, Input, Output, State
from dateutil.relativedelta import relativedelta
from path import Path

from bte_utils import read_image_s3
from bte_category_page_data_and_plots import *
from bte_market_trend_page_data_and_plots import *
from bte_product_page_data_and_plots import *

# assign default values
# px.defaults.template = "plotly_dark"

USERNAME_PASSWORD_PAIRS = [
    ['user', 'pwd123'], ['meiyume', 'pwd123']
]

# read and encode logo image
logo = 'assets/bte_logo.png'
logo_base64 = base64.b64encode(open(logo, 'rb').read()).decode('ascii')

# Create Dash Application
external_stylesheets = [dbc.themes.LUX,
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
    'fontWeight': 'bold',
    'border': 'solid 1px'
    # 'margin-left': '26rem',
    # 'margin-right': '2rem'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'}


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
                            style={'fontSize': 40,
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
                        "More pages", header=True, style={'fontSize': '18px'}),
                    dbc.DropdownMenuItem(
                        "Market Trends", href="/page-2", style={'fontSize': '18px'}),
                    dbc.DropdownMenuItem(
                        "Develop New Products", href="/page-3", style={'fontSize': '18px'}),
                    dbc.DropdownMenuItem(
                        "Improve Existing Products", href="/page-4", style={'fontSize': '18px'}),
                ],
                style={'fontSize': '25px'},
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
                            # className="lead",
                            style={'fontSize': '15', 'case': 'block',
                                   'fontName': 'Gotham'}
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
                    dbc.NavLink("Market Trend",
                                href="/page-2", id="page-2-link"),
                    dbc.NavLink("Category Insights", href="/page-3",
                                id="page-3-link"),
                    dbc.NavLink("Product KnowAll", href="/page-4",
                                id="page-4-link"),
                    dbc.NavLink("Ingredient Inside", href="/page-5",
                                id="page-5-link"),
                    dbc.NavLink("Social Media Trend", href="/page-6",
                                id="page-6-link"),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
        html.Div(),
        html.P('Data is correct as of 1st August 2020')
    ],
    id="sidebar",
    style={'position': 'flexible'}
)
'''
sidebar = html.Div(
    [html.Img(
        src=f'data:image/png;base64,{logo_base64}', height='250px', width='200px'),
        html.Hr(),
        html.P(
            "Turn unstructured data to structured insights using Natural Language Processing and Deep Learning.",
            className="lead",
            style={'fontSize': '24', 'case': 'block'}
    ),
        dbc.Nav(
            [
                dbc.NavLink("Beauty Trend Engine Landing Page",
                            href="/page-1", id="page-1-link"),
                dbc.NavLink("Market Trend Page",
                            href="/page-2", id="page-2-link"),
                dbc.NavLink("Category Page", href="/page-3", id="page-3-link"),
                dbc.NavLink("Review Page", href="/page-4", id="page-4-link"),
            ],
            vertical=True,
            pills=True,
    ),
    ],
    style=SIDEBAR_STYLE,
)
'''

content = html.Div(id="page-content")

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="output-clientside"),
        dbc.Row(
            dbc.Col(
                navbar,
                width={'size': 12}
            )
        ),
        sidebar,
        content
    ]
)


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
            html.H2('Market Trends by Categories and Product Launches',
                    style={'color': 'black',
                           #    'border': '0.5px grey dotted',
                           'width': 'auto',
                           },
                    className="row pretty_container"
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
                                         options=market_trend_page_source_options,
                                         multi=False,
                                         value='us',
                                         style={'fontSize': 14,
                                                'width': '50%'},
                                         placeholder='Select Geography',
                                         clearable=False),
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
                                                max_date_allowed=dt.today(),
                                                start_date=default_start_date,
                                                end_date=default_end_date,
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
                                         options=market_trend_page_category_options,
                                         multi=True,
                                         value=review_trend_category_df.category.unique().tolist(),
                                         style={'fontSize': 14,
                                                'width': '100%'},
                                         placeholder='Select Category',
                                         clearable=False)
                        ],
                        style={'display': 'inline-block',
                               'verticalAlign': 'top',
                               'width': '50%'}
                    )
                ],
                style={'display': 'inline-block',
                       'verticalAlign': 'top',
                       'width': '100%'},
                className="row pretty_container"
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
                                            ],
                                            className="pretty_container"
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
                                            ],
                                            className="pretty_container"
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
                                            ],
                                            className="pretty_container"
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
                                            ],
                                            className="pretty_container"
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
                                                dcc.Graph(id='product_launch_trend_category',
                                                          figure=product_launch_trend_category_figure,
                                                          ),
                                            ],
                                            className="row pretty_container"
                                        ),
                                        dbc.Row(
                                            [
                                                html.Div(id='product_trend_category_name',
                                                         style={'fontSize': 24,
                                                                'textAlign': 'center',
                                                                'fontFamily': "Gotham",
                                                                'verticalAlign': 'top'
                                                                }
                                                         ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Div(dcc.Graph(id='product_launch_trend_subcategory',
                                                                   figure=product_launch_trend_subcategory_figure,
                                                                   )
                                                         )
                                            ],
                                            className="row pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(id='product_launch_intensity_category',
                                                          figure=product_launch_intensity_category_figure,
                                                          ),
                                            ],
                                            className="row pretty_container"
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
                                        dcc.Graph(id='ingredient_launch_trend_category',
                                                  figure=new_ingredient_trend_category_figure,
                                                  ),
                                    ],
                                    className="row pretty_container"
                                ),
                                dbc.Row(
                                    [
                                        html.Div(id='ingredient_trend_category_name',
                                                 style={'fontSize': 24,
                                                        'textAlign': 'center',
                                                        'fontFamily': "Gotham",
                                                        'verticalAlign': 'top'
                                                        }
                                                 ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='ingredient_launch_trend_subcategory',
                                                  figure=new_ingredient_trend_product_type_figure,
                                                  )
                                    ],
                                    className="row pretty_container"
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
        id="mainContainer",
        style={'fontFamily': 'Gotham', "display": "flex",
               "flex-direction": "column"},
    )


def category_page_layout():
    packaging_filtered_df = cat_page_item_package_oz_df[['item_size', 'product_count']][
        (cat_page_item_package_oz_df.source == 'us') &
        (cat_page_item_package_oz_df.category == 'travel-size-toiletries') &
        (cat_page_item_package_oz_df.product_type == 'vitamins-for-hair-skin-nails')]

    top_products_df = cat_page_top_products_df[['brand', 'product_name', 'adjusted_rating',
                                                'first_review_date', 'small_size_price', 'big_size_price']][
        (cat_page_top_products_df.source == 'us') &
        (cat_page_top_products_df.category == 'travel-size-toiletries') &
        (cat_page_top_products_df.product_type == 'vitamins-for-hair-skin-nails')]

    new_products_detail_df = cat_page_new_products_details_df[['brand', 'product_name', 'adjusted_rating', 'first_review_date',
                                                               'small_size_price', 'big_size_price', 'reviews']][
        (cat_page_new_products_details_df.source == 'us') &
        (cat_page_new_products_details_df.category == 'skincare') &
        (cat_page_new_products_details_df.product_type ==
         'anti-aging-skin-care')
    ]

    new_ingredients_df = cat_page_new_ingredients_df[
        (cat_page_new_ingredients_df.source == 'us') &
        (cat_page_new_ingredients_df.category == 'makeup-cosmetics') &
        (cat_page_new_ingredients_df.product_type ==
         'setting-powder-face-powder')
    ].sort_values(by='adjusted_rating', ascending=False)[['brand', 'product_name', 'ingredient', 'ingredient_type',
                                                          'ban_flag']].reset_index(drop=True)

    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    html.H2('Product, Pricing and Market Position Analysis by Category/Subcategory',
                            style={'color': 'black',
                                   #    'border': '0.5px grey dotted',
                                   'width': 'auto',
                                   },
                            className="row pretty_container"
                            )
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H3('Select Geography'),
                                dcc.Dropdown(id='cat_page_source',
                                             options=category_page_source_options,
                                             multi=False,
                                             value='us',
                                             style={'fontSize': 14},
                                             placeholder='Select Geography',
                                             clearable=False),
                            ],
                        ),
                        width=3
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3('Select Category',
                                        style={
                                            'paddingRight': '30px'}
                                        ),
                                dcc.Dropdown(id='cat_page_category',
                                             options=category_page_category_options,
                                             multi=False,
                                             style={'fontSize': 14,
                                                    'width': '100%'},
                                             placeholder='Select Category',
                                             value='skincare',
                                             clearable=False)
                            ],
                        ),
                        width=4
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3('Select Subcategory',
                                        style={
                                            'paddingRight': '30px'}
                                        ),
                                dcc.Dropdown(id='cat_page_product_type',
                                             options=category_page_product_type_options,
                                             multi=False,
                                             style={'fontSize': 14,
                                                    'width': '100%'},
                                             placeholder='Select Subcategory',
                                             )
                            ],
                        ),
                        width=5
                    ),
                ],
                className="row pretty_container"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3('Product Analysis',
                                                    style={
                                                        'paddingRight': '30px'}
                                                    )
                                        ]
                                    ),
                                    html.Hr(),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H5(id="distinct_brands_text"),
                                                 html.P("Distinct Brands")],
                                                id="distinct_brands",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="distinct_products_text"),
                                                 html.P("Distinct Products")],
                                                id="distinct_products",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="product_variations_text"),
                                                 html.P("Product Variations")],
                                                id="product_variations",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="new_products_text"),
                                                 html.P("New Products")],
                                                id="new_products",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="info-container",
                                        className="container-display",
                                    )
                                ],
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3('Pricing Analysis',
                                                    style={
                                                        'paddingRight': '30px'}
                                                    )
                                        ]
                                    ),
                                    html.Hr(),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H5(id="min_price_text"),
                                                 html.P("Min Price")],
                                                id="min_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="max_price_text"),
                                                 html.P("Max Price")],
                                                id="max_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="avg_low_price_text"),
                                                 html.P("Avg Low Price")],
                                                id="avg_low_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="avg_high_price_text"),
                                                 html.P("Avg High Price")],
                                                id="avg_high_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H5(id="avg_item_price_text"),
                                                 html.P("Avg Item Price")],
                                                id="avg_item_price",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="info-container",
                                        className="container-display",
                                    )
                                ],
                            )
                        ]
                    )
                ],
                className="row pretty_container"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3('Package Analysis')
                                ]
                            ),
                            html.Hr(),
                            dash_table.DataTable(
                                id='product_package_data_table',
                                columns=[
                                    {"name": i, "id": i, "deletable": False,
                                     "selectable": True, "hideable": False}
                                    for i in ['item_size', 'product_count']
                                ],
                                data=packaging_filtered_df.to_dict(
                                    'records'),  # the contents of the table
                                editable=False,              # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",         # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],        # ids of columns that user selects
                                selected_rows=[],           # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="native",
                                page_current=0,             # page number that user is on
                                page_size=10,                # number of rows visible per page
                                style_cell={                # ensure adequate header width when text is shorter than cell's text
                                    'minWidth': 60, 'maxWidth': 60, 'width': 60, 'fontSize': 13, 'font-family': 'Gotham'
                                },
                                # style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                                #     {
                                #         'if': {'column_id': c},
                                #         'textAlign': 'left'
                                #     } for c in ['country', 'iso_alpha3']
                                # ],
                                style_data={                # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                }
                            )
                        ],
                        width=3,
                        className="pretty_container"
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3('Top Products by Adjusted Rating')
                                ]
                            ),
                            html.Hr(),
                            dash_table.DataTable(
                                id='top_products_data_table',
                                columns=[
                                    {"name": i, "id": i, "deletable": False,
                                     "selectable": True, "hideable": False}
                                    for i in top_products_df.columns
                                ],
                                data=top_products_df.to_dict(
                                    'records'),  # the contents of the table
                                editable=False,              # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",         # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],        # ids of columns that user selects
                                selected_rows=[],           # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="native",
                                page_current=0,             # page number that user is on
                                page_size=8,                # number of rows visible per page
                                style_cell={                # ensure adequate header width when text is shorter than cell's text
                                    'minWidth': 60, 'maxWidth': 95, 'width': 60, 'fontSize': 13, 'font-family': 'Gotham'
                                },
                                style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                                    {
                                        'if': {'column_id': 'product_name'},
                                        'textAlign': 'left'
                                    },
                                    {
                                        'if': {'column_id': 'brand'},
                                        'textAlign': 'left'
                                    },
                                    {
                                        'if': {'column_id': 'product_name'},
                                        'minWidth': 120, 'maxWidth': 160, 'width': 160
                                    },
                                    {
                                        'if': {'column_id': 'brand'},
                                        'minWidth': 100, 'maxWidth': 120, 'width': 120
                                    }
                                ],
                                style_data={                # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                }
                            )
                        ],
                        width=8,
                        className="pretty_container"
                    )
                ],
                className="row flex-display pretty_container"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3('New Products to Market')
                                ]
                            ),
                            html.Hr(),
                            dash_table.DataTable(
                                id='new_products_data_table',
                                columns=[
                                    {"name": i, "id": i, "deletable": False,
                                     "selectable": True, "hideable": False}
                                    for i in new_products_detail_df.columns
                                ],
                                data=new_products_detail_df.to_dict(
                                    'records'),  # the contents of the table
                                editable=False,              # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",         # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],        # ids of columns that user selects
                                selected_rows=[],           # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="native",
                                page_current=0,             # page number that user is on
                                page_size=10,                # number of rows visible per page
                                style_cell={                # ensure adequate header width when text is shorter than cell's text
                                    'minWidth': 80, 'maxWidth': 80, 'width': 80, 'fontSize': 13, 'font-family': 'Gotham'
                                },
                                style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                                    {
                                        'if': {'column_id': 'product_name'},
                                        'textAlign': 'left'
                                    },
                                    {
                                        'if': {'column_id': 'brand'},
                                        'textAlign': 'left'
                                    },
                                    {
                                        'if': {'column_id': 'product_name'},
                                        'minWidth': 120, 'maxWidth': 160, 'width': 160
                                    },
                                    {
                                        'if': {'column_id': 'brand'},
                                        'minWidth': 100, 'maxWidth': 110, 'width': 110
                                    }
                                ],
                                style_data={                # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                }
                            )
                        ],
                        width=12,
                        className="pretty_container"
                    ),

                ],
                className="row pretty_container"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3('New Ingredients to Market')
                                ]
                            ),
                            html.Hr(),
                            dash_table.DataTable(
                                id='new_ingredients_data_table',
                                columns=[
                                    {"name": i, "id": i, "deletable": False,
                                     "selectable": True, "hideable": False}
                                    for i in new_ingredients_df.columns
                                ],
                                data=new_ingredients_df.to_dict(
                                    'records'),  # the contents of the table
                                editable=False,              # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",         # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],        # ids of columns that user selects
                                selected_rows=[],           # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="native",
                                page_current=0,             # page number that user is on
                                page_size=10,                # number of rows visible per page
                                style_cell={                # ensure adequate header width when text is shorter than cell's text
                                    'minWidth': 120, 'maxWidth': 120, 'width': 120, 'textAlign': 'left', 'fontSize': 13, 'font-family': 'Gotham'
                                },
                                style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                                    {
                                        'if': {'column_id': 'product_name'},
                                        'minWidth': 160, 'maxWidth': 160, 'width': 160,
                                    },
                                    {
                                        'if': {'column_id': 'ban_flag'},
                                        'minWidth': 60, 'maxWidth': 60, 'width': 60,
                                    },
                                    {
                                        'if': {'column_id': 'ingredient'},
                                        'minWidth': 160, 'maxWidth': 160, 'width': 160,
                                    }
                                ],
                                style_data={                # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                }
                            )
                        ],
                        width=12,
                        className="pretty_container"
                    ),



                ],
                className="row pretty_container"
            ),
            html.Div(
                [
                    html.H3(
                        'Review Distribution by User Attributes'),
                    html.Div(
                        [
                            html.H5('Select User Attribute'),
                            dcc.Dropdown(id='cat_page_user_attribute',
                                         options=category_page_user_attribute_options,
                                         multi=False,
                                         value='age',
                                         style={'fontSize': 14},
                                         placeholder='Select User Attribute',
                                         clearable=False,
                                         ),
                        ],
                        # className="four columns",
                        style={'width': '30%'}
                    ),
                    html.Hr(),
                    dcc.Graph(id='cat_page_reviews_by_attribute',
                              figure=cat_page_user_attribute_figure)
                ],
                className="pretty_container"
            ),

        ],
        id="mainContainer",
        style={'fontFamily': 'Gotham', "display": "flex",
               "flex-direction": "column"},
    )


def product_page_layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H2('Product User Opinion and Pricing Analysis Over Time',
                                style={'color': 'black',
                                       #    'border': '0.5px grey dotted',
                                       'width': 'auto',
                                       },
                                className="row pretty_container"
                                )
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H5('Select Geography'),
                                    dcc.Dropdown(id='prod_page_source',
                                                 options=product_page_source_options,
                                                 multi=False,
                                                 value='us',
                                                 style={'fontSize': '16px'},
                                                 placeholder='Select Geography',
                                                 clearable=False),
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5('Select Product',
                                            style={
                                                'paddingRight': '30px'}
                                            ),
                                    dcc.Dropdown(id='prod_page_product',
                                                 options=product_page_product_name_options,
                                                 multi=False,
                                                 style={'fontSize': '16px',
                                                        'width': '100%'},
                                                 placeholder='Select Product',
                                                 )
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5('Select Date Range',
                                            # style={
                                            #     'paddingRight': '20px'}
                                            ),
                                    dcc.DatePickerRange(id='prod_page_review_month_range',
                                                        min_date_allowed=dt(
                                                            2008, 12, 1),
                                                        max_date_allowed=dt.today(),
                                                        start_date=default_start_date,
                                                        end_date=default_end_date
                                                        ),
                                    dcc.Markdown(
                                        id='prod-page-output-container-date-picker-range',
                                        style={'textAlign': 'left',
                                               'fontSize': '8'}
                                    )
                                ]
                            ),
                            html.Div(
                                [
                                    html.H5('Category',
                                            style={
                                                'paddingRight': '30px'}
                                            ),
                                    html.H5(id='prod_page_category',
                                            # style={'border': 'solid 1px',
                                            #        'border-color': 'lightgrey'},
                                            className="mini_container")
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5('Subcategory',
                                            style={
                                                'paddingRight': '30px'}
                                            ),
                                    html.H5(id='prod_page_subcategory',
                                            # style={'border': 'solid 1px',
                                            #        'border-color': 'lightgrey'},
                                            className="mini_container")

                                ],
                            ),
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Img(id='prod_page_product_image', width=700, height=400,
                                                     alt='Product image will be displayed here once available.'),
                                            html.P(id='prod_page_card_brand_name',
                                                   style={'fontSize': '16px'}
                                                   ),
                                            html.P(id='prod_page_card_product_name',
                                                   style={'fontSize': '16px'}
                                                   ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.P(id="prod_page_product_review_count",
                                                                   className="mini_container",
                                                                   style={
                                                                       'fontSize': '15px'},
                                                                   ),
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.P(id="prod_page_product_adjusted_rating",
                                                                   className="mini_container",
                                                                   style={
                                                                       'fontSize': '15px'}
                                                                   ),
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.P(id="prod_page_product_first_review_date",
                                                                   className="mini_container",
                                                                   style={
                                                                       'fontSize': '14.5px'}
                                                                   ),
                                                        ],
                                                        width=4
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                ],
                                # color="dark",   # https://bootswatch.com/default/ for more card colors
                                # # change color of text (black or white)
                                # inverse=True,
                                outline=False,  # True = remove the block colors from the background and header
                            )
                        ],
                        width=6
                    )
                ],
                className="row pretty_container",
            ),
            dcc.Tabs(
                [
                    dcc.Tab(label='Review_Analytics',
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.H4(
                                                            'Positive Review Summary'),
                                                        html.P(id='pos_review_sum',
                                                               children=[
                                                                   'Here Goes Review Summary'],
                                                               style={
                                                                   'fontName': 'Calibri', 'fontSize': '15px'},
                                                               className='mini-container'
                                                               )
                                                    ],
                                                )
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.H4(
                                                            'Negative Review Summary'),
                                                        html.P(id='neg_review_sum',
                                                               children=[
                                                                   'Here Goes Review Summary'],
                                                               style={
                                                                   'fontName': 'Calibri', 'fontSize': '15px'},
                                                               className='mini-container'
                                                               )
                                                    ],
                                                )
                                            ],
                                            width=6,
                                        )
                                    ],
                                    className="row pretty_container"
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H5('Review Overview',
                                                        style={
                                                            'margin-left': '10px'},
                                                        ),
                                            ]
                                        )
                                    ],
                                    className='mini-container'
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Row(
                                                    [
                                                        dcc.Graph(
                                                            id='review_sentiment_breakdown'),
                                                    ]
                                                ),
                                                dbc.Row(
                                                    [
                                                        dcc.Graph(
                                                            id='review_influenced_breakdown'),
                                                    ]
                                                ),
                                            ],
                                            width=3
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Row(
                                                    [
                                                        dcc.Graph(
                                                            id='review_sentiment_timeseries'),
                                                    ]
                                                ),
                                                dbc.Row(
                                                    [
                                                        dcc.Graph(
                                                            id='review_influenced_timeseries'),
                                                    ]
                                                )
                                            ],
                                            width={
                                                "size": 8, "offset": 1}
                                        )
                                    ],
                                    className="row pretty_container"
                                ),
                                dbc.Row(
                                    [
                                        dbc.Row(
                                            html.H5('Review Keyphrases',
                                                    style={'margin-left': '10px'})
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dcc.Graph(id='pos_talking_points_fig'
                                                                  )
                                                    ],
                                                    width=6
                                                ),
                                                dbc.Col(
                                                    [
                                                        dcc.Graph(
                                                            id='neg_talking_points_fig'
                                                        )
                                                    ],
                                                    width=6
                                                )
                                            ]
                                        )
                                    ],
                                    className="row pretty_container"
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H3(
                                                    'Review Distribution by User Attributes'),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.H5('Select User Attribute:',
                                                                        )
                                                            ],
                                                            width=5,
                                                        ),
                                                        dbc.Col(
                                                            dcc.Dropdown(id='prod_page_user_attribute',
                                                                         options=prod_page_user_attribute_options,
                                                                         multi=False,
                                                                         value='age',
                                                                         style={
                                                                             'fontSize': 14},
                                                                         placeholder='Select User Attribute',
                                                                         clearable=False,
                                                                         ),
                                                        )
                                                    ],
                                                ),
                                                # html.Hr(),
                                                dcc.Graph(
                                                    id='prod_page_reviews_by_attribute')
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                html.H3(
                                                    'Review Distribution by Stars'),
                                                html.Div(),
                                                dcc.Graph(
                                                    id='prod_page_reviews_by_stars')
                                            ]
                                        )
                                    ],
                                    className="pretty_container"
                                ),
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                    dcc.Tab(label='Price_Analytics',
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H3('Price Overview',
                                                                        style={
                                                                            'paddingRight': '30px'}
                                                                        )
                                                            ]
                                                        ),
                                                        html.Hr(),
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [html.H5(id="prod_small_price_text"),
                                                                     html.P("Small Size Price")],
                                                                    id="prod_min_price",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H5(id="prod_big_price_text"),
                                                                     html.P("Big Size Price")],
                                                                    id="prod_max_price",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H5(id="prod_mrp_text"),
                                                                     html.P("MRP")],
                                                                    id="prod_mrp",
                                                                    className="mini_container",
                                                                ),
                                                            ],
                                                            id="info-container",
                                                            className="container-display",
                                                        )
                                                    ],
                                                )
                                            ],
                                            width=4
                                        ),
                                        dbc.Col(
                                            [
                                                dcc.Graph(
                                                    'prod_page_price_variation'),
                                            ]
                                        )
                                    ],
                                    className="row pretty_container"
                                )
                            ],
                            style=tab_style,
                            selected_style=tab_selected_style
                            ),
                    dcc.Tab(label='Ingredient_Analytics',
                            children=[

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
        id="mainContainer",
        style={'fontFamily': 'Gotham', "display": "flex",
               "flex-direction": "column"},
    )


@app.callback(
    [Output('prod_small_price_text', 'children'),
     Output('prod_big_price_text', 'children'),
     Output('prod_mrp_text', 'children'),
     ],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     ]
)
def display_prod_page_price_data(source: str, prod_id: str) -> Tuple[str, str, str]:
    """display_prod_page_price_data [summary]

    [extended_summary]

    Args:
        source (str): [description]
        prod_id (str): [description]

    Returns:
        Tuple[str, str, str]: [description]
    """
    smp = product_page_metadetail_data_df.small_size_price[(product_page_metadetail_data_df.source == source) &
                                                           (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    bgp = product_page_metadetail_data_df.big_size_price[(product_page_metadetail_data_df.source == source) &
                                                         (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    mrp = product_page_metadetail_data_df.mrp[(product_page_metadetail_data_df.source == source) &
                                              (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    if source == 'us':
        currency = '$'
    else:
        currency = '£'
    return f'{currency}{smp}', f'{currency}{bgp}', f'{currency}{mrp}'


@app.callback(
    Output('prod_page_reviews_by_stars', 'figure'),
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     Input('prod_page_review_month_range', 'start_date'),
     Input('prod_page_review_month_range', 'end_date')
     ])
def update_prod_page_reviews_distribution_figure(source: str, prod_id: str,
                                                 start_date: str, end_date: str) -> Tuple[go.Figure, go.Figure]:
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

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string) &
        (prod_page_review_sentiment_influence_df.review_date <= end_date_string)]

    star_fig = create_prod_page_reviews_distribution_figure(
        data=data, prod_id=prod_id)
    return star_fig


@app.callback(Output('prod_page_reviews_by_attribute', 'figure'),
              [Input("prod_page_source", "value"),
               Input('prod_page_product', 'value'),
               Input('prod_page_user_attribute', 'value'),
               ])
def update_prod_page_reviews_by_user_attribute_figure(source: str, prod_id: str,
                                                      user_attribute: str) -> go.Figure:
    """update_prod_page_reviews_by_user_attribute_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        prod_id (str): [description]
        user_attribute (str): [description]

    Returns:
        go.Figure: [description]
    """
    fig = create_prod_page_reviews_by_user_attribute_figure(
        prod_id=prod_id, user_attribute=user_attribute)
    return fig


@app.callback(
    dash.dependencies.Output(
        'prod-page-output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('prod_page_review_month_range', 'start_date'),
     dash.dependencies.Input('prod_page_review_month_range', 'end_date')])
def date_selection_text(start_date: str, end_date: str) -> str:
    """date_selection_text [summary]

    [extended_summary]

    Args:
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        str: [description]
    """
    return 'Minimum start date is 12/01/2008. \n You can write in MM/DD/YYYY format in the date box to filter.'


@app.callback(
    [Output('review_sentiment_timeseries', 'figure'),
     Output('review_influenced_timeseries', 'figure')],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     Input('prod_page_review_month_range', 'start_date'),
     Input('prod_page_review_month_range', 'end_date')
     ])
def update_prod_page_review_timeseries_figure(source: str, prod_id: str,
                                              start_date: str, end_date: str) -> Tuple[go.Figure, go.Figure]:
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

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string) &
        (prod_page_review_sentiment_influence_df.review_date <= end_date_string)]

    sent_fig = create_prod_page_review_timeseries_figure(data,
                                                         prod_id, 'sentiment')
    inf_fig = create_prod_page_review_timeseries_figure(data,
                                                        prod_id, 'is_influenced')
    return sent_fig, inf_fig


@app.callback(
    [Output('review_sentiment_breakdown', 'figure'),
     Output('review_influenced_breakdown', 'figure')],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     Input('prod_page_review_month_range', 'start_date'),
     Input('prod_page_review_month_range', 'end_date')
     ])
def update_prod_page_review_breakdown_figure(source: str, prod_id: str,
                                             start_date: str, end_date: str) -> Tuple[go.Figure, go.Figure]:
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

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string) &
        (prod_page_review_sentiment_influence_df.review_date <= end_date_string)]

    sent_fig = create_prod_page_review_breakdown_figure(data,
                                                        prod_id, 'sentiment')
    inf_fig = create_prod_page_review_breakdown_figure(data,
                                                       prod_id, 'is_influenced')
    return sent_fig, inf_fig


@app.callback(
    [Output('pos_talking_points_fig', 'figure'),
     Output('neg_talking_points_fig', 'figure')],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value')])
def update_prod_page_review_talking_points_figure(source: str, prod_id: str):
    pos_fig = create_prod_page_review_talking_points_figure(
        prod_page_review_talking_points_df, prod_id, 'pos_talking_points')
    neg_fig = create_prod_page_review_talking_points_figure(
        prod_page_review_talking_points_df, prod_id, 'neg_talking_points')
    return pos_fig, neg_fig


@app.callback(
    [Output('pos_review_sum', 'children'),
     Output('neg_review_sum', 'children')],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     ])
def display_product_page_category(source: str, prod_id: str):
    pos_sum = prod_page_review_sum_df.pos_review_summary[
        prod_page_review_sum_df.prod_id == prod_id].values[0]
    neg_sum = prod_page_review_sum_df.neg_review_summary[
        prod_page_review_sum_df.prod_id == prod_id].values[0]
    return pos_sum, neg_sum


@app.callback(
    Output('prod_page_product_image', 'src'),
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value')])
def update_prod_page_img_src(source: str, prod_id: str):
    prod_img_path = read_image_s3(prod_id=prod_id)
    encoded_image = base64.b64encode(open(prod_img_path, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())


@app.callback(
    [Output('prod_page_card_brand_name', 'children'),
     Output('prod_page_card_product_name', 'children'),
     Output('prod_page_product_review_count', 'children'),
     Output('prod_page_product_adjusted_rating', 'children'),
     Output('prod_page_product_first_review_date', 'children'),
     ],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value'),
     Input('prod_page_review_month_range', 'start_date'),
     Input('prod_page_review_month_range', 'end_date')
     ]
)
def display_product_data_in_card(source: str, prod_id: str, start_date: str, end_date: str):
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
    prod_name = product_page_metadetail_data_df.product_name[(product_page_metadetail_data_df.source == source) &
                                                             (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    brand_name = product_page_metadetail_data_df.brand[(product_page_metadetail_data_df.source == source) &
                                                       (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    reviews = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.prod_id == prod_id) &
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string) &
        (prod_page_review_sentiment_influence_df.review_date <= end_date_string)].shape[0]
    adjusted_rating = product_page_metadetail_data_df.adjusted_rating[(product_page_metadetail_data_df.source == source) &
                                                                      (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    first_review_date = product_page_metadetail_data_df.first_review_date[(product_page_metadetail_data_df.source == source) &
                                                                          (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    return (f'Brand: {brand_name}', f'Product Name: {prod_name}', f'Reviews: {reviews}',
            f'AdjustedRating: {adjusted_rating}', f'FirstReview: {first_review_date}')


@app.callback(
    [Output('prod_page_category', 'children'),
     Output('prod_page_subcategory', 'children')],
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'value')])
def display_product_page_category(source: str, prod_id: str):
    category = product_page_metadetail_data_df.category[(product_page_metadetail_data_df.source == source) &
                                                        (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    product_type = product_page_metadetail_data_df.product_type[(product_page_metadetail_data_df.source == source) &
                                                                (product_page_metadetail_data_df.prod_id == prod_id)].values[0]
    return category, product_type


@app.callback(
    Output('prod_page_product', 'options'),
    [Input('prod_page_source', 'value')]
)
def set_product_page_product_options(source: str):
    return [{'label': i[0], 'value': i[1]}
            for i in product_page_metadetail_data_df[
                ['product_name',
                 'prod_id']][product_page_metadetail_data_df.source == source
                             ].values.tolist()]


@app.callback(
    Output('prod_page_product', 'value'),
    [Input("prod_page_source", "value"),
     Input('prod_page_product', 'options')])
def set_product_page_product_value(source, available_options):
    return available_options[10]['value']


@app.callback(Output('cat_page_reviews_by_attribute', 'figure'),
              [Input("cat_page_source", "value"),
               Input("cat_page_category", "value"),
               Input("cat_page_product_type", "value"),
               Input("cat_page_user_attribute", "value")
               ]
              )
def update_reviews_by_user_attribute_figure(source: str, category: str,
                                            product_type: str,
                                            user_attribute: str) -> go.Figure:
    """update_reviews_by_user_attribute_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]
        user_attribute (str): [description]

    Returns:
        go.Figure: [description]
    """
    fig = create_reviews_by_user_attribute_figure(source=source, category=category,
                                                  product_type=product_type, user_attribute=user_attribute)

    return fig


@app.callback(Output('new_ingredients_data_table', 'data'),
              [Input("cat_page_source", "value"),
               Input("cat_page_category", "value"),
               Input("cat_page_product_type", "value")
               ]
              )
def filter_top_products_data_table(source: str, category: str, product_type: str) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    new_ingredients_df = cat_page_new_ingredients_df[
        (cat_page_new_ingredients_df.source == source) &
        (cat_page_new_ingredients_df.category == category) &
        (cat_page_new_ingredients_df.product_type == product_type)
    ].sort_values(by='adjusted_rating', ascending=False)[['brand', 'product_name', 'ingredient', 'ingredient_type',
                                                          'ban_flag']].reset_index(drop=True)

    return new_ingredients_df.to_dict('records')


@app.callback(Output('new_products_data_table', 'data'),
              [Input("cat_page_source", "value"),
               Input("cat_page_category", "value"),
               Input("cat_page_product_type", "value")
               ]
              )
def filter_top_products_data_table(source: str, category: str, product_type: str) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    new_products_detail_df = cat_page_new_products_details_df[['brand', 'product_name', 'adjusted_rating', 'first_review_date',
                                                               'small_size_price', 'big_size_price', 'reviews']][
        (cat_page_new_products_details_df.source == source) &
        (cat_page_new_products_details_df.category == category) &
        (cat_page_new_products_details_df.product_type == product_type)
    ]

    new_products_detail_df.sort_values(
        by='adjusted_rating', inplace=True, ascending=False)

    return new_products_detail_df.to_dict('records')


@app.callback(Output('top_products_data_table', 'data'),
              [Input("cat_page_source", "value"),
               Input("cat_page_category", "value"),
               Input("cat_page_product_type", "value")
               ]
              )
def filter_top_products_data_table(source: str, category: str, product_type: str) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    top_products_df = cat_page_top_products_df[['brand', 'product_name', 'adjusted_rating',
                                                'first_review_date', 'small_size_price', 'big_size_price']][
        (cat_page_top_products_df.source == source) &
        (cat_page_top_products_df.category == category) &
        (cat_page_top_products_df.product_type == product_type)]

    top_products_df.sort_values(
        by='adjusted_rating', inplace=True, ascending=False)

    return top_products_df.to_dict('records')


@app.callback(Output('product_package_data_table', 'data'),
              [Input("cat_page_source", "value"),
               Input("cat_page_category", "value"),
               Input("cat_page_product_type", "value")
               ]
              )
def filter_product_packaging_data_table(source: str, category: str, product_type: str) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    packaging_filtered_df = cat_page_item_package_oz_df[['item_size', 'product_count']][
        (cat_page_item_package_oz_df.source == source) &
        (cat_page_item_package_oz_df.category == category) &
        (cat_page_item_package_oz_df.product_type == product_type)]

    packaging_filtered_df.sort_values(
        by='product_count', inplace=True, ascending=False)

    return packaging_filtered_df.to_dict('records')


@app.callback(
    Output('cat_page_product_type', 'options'),
    [Input('cat_page_source', 'value'),
     Input('cat_page_category', 'value')])
def set_category_page_product_type_options(source: str, category: str):
    return [{'label': i, 'value': i}
            for i in cat_page_pricing_analytics_df.product_type[(cat_page_pricing_analytics_df.source == source) &
                                                                (cat_page_pricing_analytics_df.category == category)].unique()]


@app.callback(
    Output('cat_page_product_type', 'value'),
    [Input("cat_page_source", "value"),
     Input("cat_page_category", "value"),
     Input('cat_page_product_type', 'options')])
def set_category_page_product_type_value(source, category, available_options):
    return available_options[0]['value']


@app.callback(
    [
        Output("distinct_brands_text", "children"),
        Output("distinct_products_text", "children"),
        Output("product_variations_text", "children"),
        Output("new_products_text", "children"),
    ],
    [Input("cat_page_source", "value"),
     Input("cat_page_category", "value"),
     Input("cat_page_product_type", "value")],
)
def update_product_analysis_text(source: str, category: str, product_type: str) -> Tuple[str, str, str, str]:
    """update_text [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        Tuple[str, str, str, str]: [description]
    """
    dist_list = cat_page_distinct_brands_products_df[[
        'distinct_brands', 'distinct_products']][
        (cat_page_distinct_brands_products_df.source == source) &
        (cat_page_distinct_brands_products_df.category == category) &
        (cat_page_distinct_brands_products_df.product_type == product_type)].values.tolist()[0]

    new_products_list = cat_page_new_products_count_df.new_product_count[
        (cat_page_new_products_count_df.source == source) &
        (cat_page_new_products_count_df.category == category) &
        (cat_page_new_products_count_df.product_type == product_type)].values.tolist()

    product_variations = cat_page_item_variations_price_df.product_variations[
        (cat_page_item_variations_price_df.source == source) &
        (cat_page_item_variations_price_df.category == category) &
        (cat_page_item_variations_price_df.product_type == product_type)].values.tolist()
    if len(new_products_list) == 0:
        new_products = 0
    else:
        new_products = new_products_list[0]

    return dist_list[0], dist_list[1], product_variations[0], new_products


@app.callback(
    [
        Output("min_price_text", "children"),
        Output("max_price_text", "children"),
        Output("avg_low_price_text", "children"),
        Output("avg_high_price_text", "children"),
        Output("avg_item_price_text", "children")
    ],
    [Input("cat_page_source", "value"),
     Input("cat_page_category", "value"),
     Input("cat_page_product_type", "value")],
)
def update_pricing_analysis_text(source: str, category: str, product_type: str) -> Tuple[str, str, str, str]:
    """update_text [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        Tuple[str, str, str, str]: [description]
    """
    pricing_data = [f'${p}' if source == 'us' else f'£{p}'
                    for p in cat_page_pricing_analytics_df[['min_price', 'max_price', 'avg_low_price', 'avg_high_price']]
                    [(cat_page_pricing_analytics_df.source == source) &
                     (cat_page_pricing_analytics_df.category == category) &
                     (cat_page_pricing_analytics_df.product_type == product_type)].values.tolist()[0]
                    ]
    item_price = [f'${p}' if source == 'us' else f'£{p}'
                  for p in cat_page_item_variations_price_df.avg_item_price[
                      (cat_page_item_variations_price_df.source == source) &
                      (cat_page_item_variations_price_df.category == category) &
                      (cat_page_item_variations_price_df.product_type == product_type)].values.tolist()]

    return pricing_data[0], pricing_data[1], pricing_data[2], pricing_data[3], item_price[0]


@app.callback(Output('category_trend', 'figure'),
              inputs=[Input('source', 'value'),
                      Input('category', 'value'),
                      Input('review_month_range', 'start_date'),
                      Input('review_month_range', 'end_date')
                      ]
              )
def update_category_review_trend_figure(source: str, category: list, start_date: str, end_date: str) -> go.Figure:
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
def update_category_influenced_review_trend_figure(source: str, category: list, start_date: str, end_date: str) -> go.Figure:
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
def influenced_display_click_data(clickData) -> str:
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
def display_click_data(clickData) -> str:
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
def update_product_type_review_trend_figure(source: str, clickData, start_date: str, end_date: str) -> go.Figure:
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
    product_type_count = len(review_trend_product_type_df[(review_trend_product_type_df.category ==
                                                           category) & (review_trend_product_type_df.source == source)].product_type.unique())
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
def update_product_type_influenced_review_trend_figure(source: str, clickData, start_date: str, end_date: str) -> go.Figure:
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
    product_type_count = len(influenced_review_trend_product_type_df[(influenced_review_trend_product_type_df.category
                                                                      == category) &
                                                                     (influenced_review_trend_product_type_df.source
                                                                      == source)].product_type.unique())
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
def date_selection_text(start_date: str, end_date: str) -> str:
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
def update_category_product_launch_figure(source: str, category: list, start_date: str, end_date: str) -> go.Figure:
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
def display_click_data_product_trend(clickData) -> str:
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
        return ('Selected Category: bath-body')


@app.callback(Output('product_launch_trend_subcategory', 'figure'),
              [Input('source', 'value'),
               Input('product_launch_trend_category', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_product_launch_figure(source: str, clickData, start_date: str, end_date: str) -> go.Figure:
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
def update_product_launch_intensity_figure(source: str, category: list, start_date: str, end_date: str) -> go.Figure:
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
def update_category_new_ingredient_trend_figure(source: str, category: list, start_date: str, end_date: str) -> go.Figure:
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
def display_click_data_ingredient_trend(clickData) -> str:
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
        return ('Selected Category: bath-body')


@app.callback(Output('ingredient_launch_trend_subcategory', 'figure'),
              [Input('source', 'value'),
               Input('ingredient_launch_trend_category', 'clickData'),
               Input('review_month_range', 'start_date'),
               Input('review_month_range', 'end_date')]
              )
def update_product_type_new_ingredient_trend_figure(source: str, clickData, start_date: str, end_date: str) -> go.Figure:
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
    [Output(f"page-{i}-link", "active") for i in range(1, 7)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False, False, False
    return [pathname == f"/page-{i}" for i in range(1, 7)]


@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        # html.P("This is the content of page 1!")
        return landing_page_layout()
    elif pathname == "/page-2":
        return market_trend_page_layout()
    elif pathname == "/page-3":
        return category_page_layout()
    elif pathname == "/page-4":
        return product_page_layout()
    elif pathname == "/page-5":
        return 'check this out. wip. yipee ki kay'
    elif pathname == "/page-6":
        return 'check this out. wip. yipee ki kay'
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
    # app.run_server(debug=True)
