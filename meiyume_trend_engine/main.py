""" This app creates a sidebar layout using inline style arguments and the dbc.Nav component for Beauty Trend Engine.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.
"""
import re
from datetime import datetime as dt
from typing import Tuple

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from bte_category_page_data_and_plots import *
from bte_ingredient_page_data_and_plots import *
from bte_market_trend_page_data_and_plots import *
from bte_product_page_data_and_plots import *
from bte_utils import read_file_s3, read_image_s3
from settings import *

# assign default values
# px.defaults.template = "plotly_dark"
# landing page data
# PACKAGING_SIZE = "Packaging Size"
# NUMBER_OF_PRODUCTS = "Number of Products"
# PRODUCT_DESCRIPTION = "Product Description"
# PRODUCT_RATING_ADJUSTED = "Product Rating (Adjusted)"
# DATE_FIRST_REVIEWED = "Date (First Reviewed)"
# PRICE_LOW = "Price (Low)"
# PRICE_HIGH = "Price (High)"
PACKAGING_SIZE = "item_size"
NUMBER_OF_PRODUCTS = "product_count"
PRODUCT_DESCRIPTION = "product_name"
PRODUCT_RATING_ADJUSTED = "adjusted_rating"
DATE_FIRST_REVIEWED = "first_review_date"
PRICE_LOW = "small_size_price"
PRICE_HIGH = "big_size_price"

lp_df = read_file_s3(filename="landing_page_data", file_type="feather")
# pd.read_feather(dash_data_path/'landing_page_data')

USERNAME_PASSWORD_PAIRS = [["user", "pwd123"], ["meiyume", "pwd123"]]

# read and encode logo image
logo_url = f"https://{S3_BUCKET}.s3-{S3_REGION}.amazonaws.com/{S3_PREFIX}/static/assets/bte_logo.png"

# Create Dash Application
external_stylesheets = [
    dbc.themes.LUX,
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://use.fontawesome.com/releases/v5.10.2/css/all.css",
]
external_scripts = [
    "https://www.googletagmanager.com/gtag/js?id=UA-180588565-1",
]

app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# create tab and sidebar css style sheets
tabs_styles = {"height": "44px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
    "border": "solid 1px"
    # 'margin-left': '26rem',
    # 'margin-right': '2rem'
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#119DFF",
    "color": "white",
    "padding": "6px",
}
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
                    html.H1(
                        "Beauty Trend Engine",
                        className="display-4",
                        style={
                            "fontSize": 40,
                            "color": "white",
                            #    'backgroundColor': 'white',
                            "fontFamily": "GildaDisplay",
                            "fontWeight": "bold",
                            "textShadow": "#fc0 1px 0 10px",
                        },
                    ),
                    # dbc.NavbarBrand("Navbar", className="ml-2"),
                ]
            ),
            width={"size": 5, "offset": 2},
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
        dbc.Col(
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(
                        "More pages", header=True, style={"fontSize": "18px"}
                    ),
                    dbc.DropdownMenuItem(
                        "Market Trends",
                        href="/page-2",
                        style={"fontSize": "18px"},
                    ),
                    dbc.DropdownMenuItem(
                        "Develop New Products",
                        href="/page-3",
                        style={"fontSize": "18px"},
                    ),
                    dbc.DropdownMenuItem(
                        "Improve Existing Products",
                        href="/page-4",
                        style={"fontSize": "18px"},
                    ),
                ],
                style={"fontSize": "25px"},
                in_navbar=True,
                label="Select Application",
            ),
            width={"size": 2},
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
                        html.Img(src=logo_url, height="250px", width="200px"),
                        # html.Hr(),
                    ]
                ),
                dbc.Col(
                    [
                        html.Button(
                            "|||",
                            # use the Bootstrap navbar-toggler classes to style
                            className="navbar-toggler navbarToggleButton",
                            # the navbar-toggler classes don't set color,
                            id="sidebar-toggle",
                        ),
                    ],
                    # the column containing the toggle will be only as wide as the
                    # toggle, resulting in the toggle being right aligned
                    width={"size": "auto"},
                    # vertically align the toggle in the center
                ),
            ],
            style={"marginLeft": -20},
        )
    ],
)

last_scraped_date = pd.to_datetime(lp_df["latest_scraped_date"].values[0]).strftime(
    "%d %B %Y"
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
                    dbc.NavLink(
                        "Beauty Trend Engine", href="/page-1", id="page-1-link"
                    ),
                    dbc.NavLink("Market Trend", href="/page-2", id="page-2-link"),
                    dbc.NavLink("Category Insights", href="/page-3", id="page-3-link"),
                    dbc.NavLink("Product Insights", href="/page-4", id="page-4-link"),
                    dbc.NavLink(
                        "Ingredient Insights", href="/page-5", id="page-5-link"
                    ),
                    # dbc.NavLink("Social Media Trend", href="/page-6", id="page-6-link"),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
        html.Div(),
        html.P(
            id="last_scraped_date",
            children=[f"Data is accurate as of: {last_scraped_date}"],
        ),
    ],
    id="sidebar",
)
"""
sidebar = html.Div(
    [html.Img(
        src=f'data:image/png;base64,{logo_base64}', height='250px', width='200px'),
        # html.Hr(),
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
"""

content = html.Div(id="page-content")

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="output-clientside"),
        # dbc.Row(
        #     dbc.Col(
        #         navbar,
        #         width={'size': 12}
        #     )
        # ),
        sidebar,
        content,
    ]
)


def landing_page_layout():
    return html.Div(
        children=[
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Img(
                                        id="landing_page_logo",
                                        width=200,
                                        height=300,
                                        src=logo_url,
                                        alt="Product image will be displayed here once available.",
                                    ),
                                ],
                                width={"size": 6, "offest": 3},
                                # className='pretty_container'
                            )
                        ],
                        justify="center",
                        style={"opacity": 0.90},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.P(
                                                        "Turn unstructured data to structured insights using \
                                                         Natural Language Processing and Deep Learning.",
                                                        # className="lead",
                                                        className="pageSubtitle",
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "align-items": "center",
                                                    "justify-content": "center",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    html.H2(
                                                        "Total Data Gathered",
                                                        className="mini_container",
                                                        style={
                                                            "fontFamily": "GildaDisplay"
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "fontFamily": "GildaDisplay",
                                                    "fontSize": "20pt",
                                                },
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                id="lp_total_brands",
                                                                children=[
                                                                    mark_digit(
                                                                        lp_df[
                                                                            "brands"
                                                                        ].values[0]
                                                                    )
                                                                ],
                                                                className="gildaDisplay22pt",
                                                                style={
                                                                    "fontFamily": "GildaDisplay",
                                                                },
                                                            ),
                                                            html.H6(
                                                                "Brands",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            ),
                                                        ],
                                                        id="distinct_brands",
                                                        className="mini_container gothamBook15pt",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                id="lp_total_products",
                                                                children=[
                                                                    mark_digit(
                                                                        lp_df[
                                                                            "products"
                                                                        ].values[0]
                                                                    )
                                                                ],
                                                                className="gildaDisplay22pt",
                                                            ),
                                                            html.H6(
                                                                "Products",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            ),
                                                        ],
                                                        id="distinct_products",
                                                        className="mini_container gothamBook15pt",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                id="lp_total_ingredients",
                                                                children=[
                                                                    mark_digit(
                                                                        lp_df[
                                                                            "ingredients"
                                                                        ].values[0]
                                                                    )
                                                                ],
                                                                className="gildaDisplay22pt",
                                                            ),
                                                            html.H6(
                                                                "Ingredients",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            ),
                                                        ],
                                                        id="distinct_ingredients",
                                                        className="mini_container gothamBook15pt",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                id="lp_total_reviews",
                                                                children=[
                                                                    mark_digit(
                                                                        lp_df[
                                                                            "reviews"
                                                                        ].values[0]
                                                                    )
                                                                ],
                                                                className="gildaDisplay22pt",
                                                            ),
                                                            html.H6(
                                                                "Reviews",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            ),
                                                        ],
                                                        id="distinct_reviews",
                                                        className="mini_container gothamBook15pt",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                id="lp_total_images",
                                                                children=[
                                                                    mark_digit(
                                                                        lp_df[
                                                                            "images"
                                                                        ].values[0]
                                                                    )
                                                                ],
                                                                className="gildaDisplay22pt",
                                                            ),
                                                            html.H6(
                                                                "Images",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            ),
                                                        ],
                                                        id="distinct_images",
                                                        className="mini_container gothamBook15pt",
                                                    ),
                                                ],
                                                id="info-container",
                                                className="container-display",
                                                justify="center",
                                            ),
                                        ],
                                    )
                                ],
                                width={
                                    "size": 8,
                                    # "offest": 3,
                                },
                            )
                        ],
                        justify="center",
                        style={"backgroundColor": "white"},
                    ),
                ],
                id="mainContainer",
                style={
                    "verticalAlign": "middle",
                    "textAlign": "center",
                    "background-image": "url(assets/landing_page_bg.jpg)",
                    "background-size": "cover",
                    "width": "100%",
                    "height": "100%",
                    "top": "0px",
                    "left": "0px",
                    "fontFamily": "GothamLight",
                    "display": "absolute",
                    "flex-direction": "column",
                },
            )
        ],
    )


def market_trend_page_layout():
    """market_trend_page_layout [summary]

    [extended_summary]

    Returns:
        html: market trend page layout
    """
    return html.Div(
        [
            html.H2(
                "What is happening in the market?",
                style={
                    "color": "black",
                    #    'border': '0.5px grey dotted',
                    "width": "auto",
                    "fontFamily": "GildaDisplay",
                },
                className="row pretty_container",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Geography",
                                style={
                                    "paddingRight": "15px",
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            dcc.Dropdown(
                                id="source",
                                options=market_trend_page_source_options,
                                multi=False,
                                value="us",
                                style={"fontSize": 14, "width": "50%"},
                                placeholder="Select Geography",
                                clearable=False,
                            ),
                        ],
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "width": "25%",
                        },
                    ),
                    html.Div(
                        [
                            html.H3(
                                "Date Range",
                                style={
                                    "paddingRight": "20px",
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            dcc.DatePickerRange(
                                id="review_month_range",
                                min_date_allowed=dt(2008, 12, 1),
                                max_date_allowed=dt.today(),
                                start_date=default_start_date,
                                end_date=default_end_date,
                            ),
                            dcc.Markdown(
                                id="output-container-date-picker-range",
                                style={"textAlign": "left", "fontSize": "10"},
                            ),
                        ],
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "width": "25%",
                        },
                    ),
                    html.Div(
                        [
                            html.H3(
                                "Category",
                                style={
                                    "paddingRight": "30px",
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            dcc.Dropdown(
                                id="category",
                                options=market_trend_page_category_options,
                                multi=True,
                                value=review_trend_category_df.category.unique().tolist(),
                                style={"fontSize": 14, "width": "100%"},
                                placeholder="Select Category",
                                clearable=False,
                            ),
                        ],
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "width": "50%",
                        },
                    ),
                ],
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "width": "100%",
                },
                className="row pretty_container",
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="User Reviews",
                        children=[
                            html.Div(
                                [
                                    html.H2(
                                        "Review Trend",
                                        style={
                                            "paddingRight": "30px",
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.H4(
                                        "Click on the line of a category to visualize trends of subcategories under it",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="category_trend",
                                                figure=category_trend_figure,
                                            ),
                                        ],
                                        className="pretty_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H3(
                                                "Review Subcategory Trend",
                                                style={
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            ),
                                            html.Div(
                                                id="category_name",
                                                style={
                                                    "fontSize": 24,
                                                    "fontFamily": "GothamLight",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="subcategory_trend",
                                            ),
                                        ],
                                        className="pretty_container",
                                    ),
                                ]
                            )
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Paid Reviews",
                        children=[
                            html.Div(
                                [
                                    html.H2(
                                        "Review Trend by Marketing Output",
                                        style={
                                            "paddingRight": "30px",
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.H4(
                                        "Click on the line of a category to visualize trends of subcategories under it",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="influenced_category_trend",
                                                figure=influenced_category_trend_figure,
                                            ),
                                        ],
                                        className="pretty_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H3(
                                                "Review Subcategory Trend by Marketing Output",
                                                style={
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            ),
                                            html.Div(
                                                id="influenced_category_name",
                                                style={
                                                    "fontSize": 24,
                                                    "fontFamily": "GothamLight",
                                                },
                                            ),
                                            # html.Hr(),
                                            dcc.Graph(
                                                id="influenced_subcategory_trend",
                                            ),
                                        ],
                                        className="pretty_container",
                                    ),
                                ]
                            )
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Product Launches",
                        children=[
                            html.H2(
                                "Product Launch Trends and Intensity by Category",
                                style={
                                    "paddingRight": "30px",
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            # html.Hr(),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="product_launch_trend_category",
                                                figure=product_launch_trend_category_figure,
                                            ),
                                        ],
                                        className="row pretty_container",
                                    ),
                                    dbc.Row(
                                        [
                                            html.Div(
                                                id="product_trend_category_name",
                                                style={
                                                    "fontSize": 24,
                                                    "textAlign": "center",
                                                    "fontFamily": "GothamLight",
                                                    "verticalAlign": "top",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                dcc.Graph(
                                                    id="product_launch_trend_subcategory",
                                                    figure=product_launch_trend_subcategory_figure,
                                                )
                                            )
                                        ],
                                        className="row pretty_container",
                                    ),
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="product_launch_intensity_category",
                                                figure=product_launch_intensity_category_figure,
                                            ),
                                        ],
                                        className="row pretty_container",
                                    ),
                                ],
                            ),
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="New Ingredients",
                        children=[
                            html.H2(
                                "Ingredient Trends by Category",
                                style={
                                    "paddingRight": "30px",
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            # html.Hr(),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="ingredient_launch_trend_category",
                                        figure=new_ingredient_trend_category_figure,
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                            dbc.Row(
                                [
                                    html.Div(
                                        id="ingredient_trend_category_name",
                                        style={
                                            "fontSize": 24,
                                            "textAlign": "center",
                                            "fontFamily": "GothamLight",
                                            "verticalAlign": "top",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="ingredient_launch_trend_subcategory",
                                        figure=new_ingredient_trend_product_type_figure,
                                    )
                                ],
                                className="row pretty_container",
                            ),
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                ],
                style=tabs_styles,
                colors={
                    "border": "white",
                    "primary": "gold",
                    "background": "cornsilk",
                },
            ),
        ],
        id="mainContainer",
        style={
            "fontFamily": "GothamLight",
            "display": "flex",
            "flex-direction": "column",
        },
    )


def category_page_layout():
    packaging_filtered_df = cat_page_item_package_oz_df[
        ["item_size", "product_count", "avg_price"]
    ][
        (cat_page_item_package_oz_df.source == "us")
        & (cat_page_item_package_oz_df.category == "travel-size-toiletries")
        & (cat_page_item_package_oz_df.product_type == "vitamins-for-hair-skin-nails")
    ]

    top_products_df = cat_page_top_products_df[
        [
            "brand",
            "product_name",
            "adjusted_rating",
            "first_review_date",
            "reviews",
            "positive_reviews",
            "negative_reviews",
        ]
    ][
        (cat_page_top_products_df.source == "us")
        & (cat_page_top_products_df.category == "travel-size-toiletries")
        & (cat_page_top_products_df.product_type == "vitamins-for-hair-skin-nails")
    ]

    new_products_detail_df = cat_page_new_products_details_df[
        [
            "brand",
            "product_name",
            "adjusted_rating",
            "first_review_date",
            "reviews",
            "positive_reviews",
            "negative_reviews",
        ]
    ][
        (cat_page_new_products_details_df.source == "us")
        & (cat_page_new_products_details_df.category == "skincare")
        & (cat_page_new_products_details_df.product_type == "anti-aging-skin-care")
    ]

    new_ingredients_df = (
        cat_page_new_ingredients_df[
            (cat_page_new_ingredients_df.source == "us")
            & (cat_page_new_ingredients_df.category == "makeup-cosmetics")
            & (cat_page_new_ingredients_df.product_type == "setting-powder-face-powder")
        ]
        .sort_values(by="adjusted_rating", ascending=False)[
            [
                "brand",
                "product_name",
                "ingredient",
                "ingredient_type",
                "ban_flag",
            ]
        ]
        .reset_index(drop=True)
    )

    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    html.H2(
                        "Product, Pricing and Market Position Analysis by Category/Subcategory",
                        style={
                            "color": "black",
                            #    'border': '0.5px grey dotted',
                            "width": "auto",
                            "fontFamily": "GildaDisplay",
                        },
                        className="row pretty_container",
                    )
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Geography",
                                    style={
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="cat_page_source",
                                    options=category_page_source_options,
                                    multi=False,
                                    value="us",
                                    style={"fontSize": 14},
                                    placeholder="Select Geography",
                                    clearable=False,
                                ),
                            ],
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Category",
                                    style={
                                        "paddingRight": "30px",
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="cat_page_category",
                                    options=category_page_category_options,
                                    multi=False,
                                    style={"fontSize": 14, "width": "100%"},
                                    placeholder="Select Category",
                                    value="skincare",
                                    clearable=False,
                                ),
                            ],
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H3(
                                    "Subcategory",
                                    style={
                                        "paddingRight": "30px",
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="cat_page_product_type",
                                    options=category_page_product_type_options,
                                    multi=False,
                                    style={"fontSize": 14, "width": "100%"},
                                    placeholder="Select Subcategory",
                                ),
                            ],
                        ),
                        width=5,
                    ),
                ],
                className="row pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3(
                                                "Product Analysis",
                                                style={
                                                    "paddingRight": "30px",
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="distinct_brands_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Unique Brands"),
                                                ],
                                                id="distinct_brands",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="distinct_products_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Unique Products"),
                                                ],
                                                id="distinct_products",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="product_variations_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Product Variations"),
                                                ],
                                                id="product_variations",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="new_products_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("New Products Launched"),
                                                ],
                                                id="new_products",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="info-container",
                                        className="container-display",
                                    ),
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
                                            html.H3(
                                                "Pricing Analysis",
                                                style={
                                                    "paddingRight": "30px",
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="min_price_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Min Price"),
                                                ],
                                                id="min_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="max_price_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Max Price"),
                                                ],
                                                id="max_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="avg_low_price_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Avg Low Price"),
                                                ],
                                                id="avg_low_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="avg_high_price_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Avg High Price"),
                                                ],
                                                id="avg_high_price",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="avg_item_price_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Avg Item Price"),
                                                ],
                                                id="avg_item_price",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="info-container",
                                        className="container-display",
                                    ),
                                ],
                            )
                        ]
                    ),
                ],
                className="row pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Packaging",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    )
                                ]
                            ),
                            dash_table.DataTable(
                                id="product_package_data_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in packaging_filtered_df.columns
                                ],
                                data=packaging_filtered_df.to_dict(
                                    "records"
                                ),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="none",
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 60,
                                    "maxWidth": 60,
                                    "width": 60,
                                    "fontSize": 13,
                                    "font-family": "GothamLight",
                                },
                                style_data={  # overflow cells' content into multiple lines
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                fixed_rows={"headers": True},
                                style_table={
                                    "height": 360,
                                    "overflow": "auto",
                                },
                            ),
                        ],
                        width=3,
                        className="pretty_container",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Top Rated Products",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    )
                                ]
                            ),
                            dash_table.DataTable(
                                id="top_products_data_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in top_products_df.columns
                                ],
                                data=top_products_df.to_dict(
                                    "records"
                                ),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="none",
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 60,
                                    "width": 80,
                                    "maxWidth": 95,
                                    "fontSize": 13,
                                    "fontFamily": "GothamLight",
                                },
                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                    {
                                        "if": {"column_id": "product_name"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "brand"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "product_name"},
                                        "minWidth": 120,
                                        "maxWidth": 160,
                                        "width": 160,
                                    },
                                    {
                                        "if": {"column_id": "brand"},
                                        "minWidth": 100,
                                        "maxWidth": 120,
                                        "width": 120,
                                    },
                                ],
                                style_data={  # overflow cells' content into multiple lines
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                fixed_rows={"headers": True},
                                style_table={
                                    "height": 360,
                                    "overflow": "auto",
                                },
                            ),
                        ],
                        width=8,
                        className="pretty_container",
                    ),
                ],
                className="row flex-display pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "New Products to Market",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    )
                                ]
                            ),
                            dash_table.DataTable(
                                id="new_products_data_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in new_products_detail_df.columns
                                ],
                                data=new_products_detail_df.to_dict(
                                    "records"
                                ),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 60,
                                    "width": 80,
                                    "maxWidth": 80,
                                    "fontSize": 13,
                                    "font-family": "GothamLight",
                                },
                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                    {
                                        "if": {"column_id": "product_name"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "brand"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "product_name"},
                                        "minWidth": 120,
                                        "maxWidth": 160,
                                        "width": 160,
                                    },
                                    {
                                        "if": {"column_id": "brand"},
                                        "minWidth": 100,
                                        "maxWidth": 110,
                                        "width": 110,
                                    },
                                ],
                                style_data={  # overflow cells' content into multiple lines
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                style_table={
                                    "overflow": "auto",
                                    "height": 200,
                                },
                            ),
                        ],
                        width=12,
                        className="pretty_container",
                    ),
                ],
                className="row pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "New Ingredients to Market",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    )
                                ]
                            ),
                            dash_table.DataTable(
                                id="new_ingredients_data_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in new_ingredients_df.columns
                                ],
                                data=new_ingredients_df.to_dict(
                                    "records"
                                ),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                filter_action="native",
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 120,
                                    "maxWidth": 120,
                                    "width": 120,
                                    "textAlign": "left",
                                    "fontSize": 13,
                                    "font-family": "GothamLight",
                                },
                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                    {
                                        "if": {"column_id": "product_name"},
                                        "minWidth": 160,
                                        "maxWidth": 160,
                                        "width": 160,
                                    },
                                    {
                                        "if": {"column_id": "ban_flag"},
                                        "minWidth": 60,
                                        "maxWidth": 60,
                                        "width": 60,
                                    },
                                    {
                                        "if": {"column_id": "ingredient"},
                                        "minWidth": 160,
                                        "maxWidth": 160,
                                        "width": 160,
                                    },
                                ],
                                style_data={
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                fixed_rows={"headers": True},
                                style_table={
                                    "height": 400,
                                    "overflow": "auto",
                                },
                            ),
                        ],
                        width=12,
                        className="pretty_container",
                    ),
                ],
                className="row pretty_container",
            ),
            html.Div(
                [
                    html.H3(
                        "Reviewer's Demographics",
                        style={
                            "fontFamily": "GildaDisplay",
                        },
                    ),
                    html.Div(
                        [
                            html.H5(
                                "User Attribute",
                                style={
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            dcc.Dropdown(
                                id="cat_page_user_attribute",
                                options=category_page_user_attribute_options,
                                multi=False,
                                value="age",
                                style={"fontSize": 14},
                                placeholder="Select User Attribute",
                                clearable=False,
                            ),
                        ],
                        # className="four columns",
                        style={"width": "30%"},
                    ),
                    # html.Hr(),
                    dcc.Graph(
                        id="cat_page_reviews_by_attribute",
                        figure=cat_page_user_attribute_figure,
                    ),
                ],
                className="pretty_container",
            ),
        ],
        id="mainContainer",
        style={
            "fontFamily": "GothamLight",
            "display": "flex",
            "flex-direction": "column",
        },
    )


def product_page_layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H2(
                            "Product User Opinion and Pricing Analysis Over Time",
                            style={
                                "color": "black",
                                #    'border': '0.5px grey dotted',
                                "width": "auto",
                                "fontFamily": "GildaDisplay",
                            },
                            className="row pretty_container",
                        )
                    )
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H5(
                                        "Geography",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="prod_page_source",
                                        options=product_page_source_options,
                                        multi=False,
                                        value="us",
                                        style={"fontSize": "16px"},
                                        placeholder="Select Geography",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        "Product",
                                        style={"paddingRight": "30px"},
                                    ),
                                    dcc.Dropdown(
                                        id="prod_page_product",
                                        options=product_page_product_name_options,
                                        multi=False,
                                        style={
                                            "fontSize": "16px",
                                            "width": "100%",
                                        },
                                        placeholder="Select Product",
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        "Date Range",
                                        style={
                                            "fontFamily": "GildaDisplay",
                                        },
                                        # style={
                                        #     'paddingRight': '20px'}
                                    ),
                                    dcc.DatePickerRange(
                                        id="prod_page_review_month_range",
                                        min_date_allowed=dt(2008, 12, 1),
                                        max_date_allowed=dt.today(),
                                        start_date=default_start_date,
                                        end_date=default_end_date,
                                    ),
                                    dcc.Markdown(
                                        id="prod-page-output-container-date-picker-range",
                                        style={
                                            "textAlign": "left",
                                            "fontSize": "8",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        "Category",
                                        style={
                                            "paddingRight": "30px",
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.H5(
                                        id="prod_page_category",
                                        # style={'border': 'solid 1px',
                                        #        'border-color': 'lightgrey'},
                                        className="mini_container",
                                        style={"fontFamily": "GildaDisplay"},
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        "Subcategory",
                                        style={
                                            "paddingRight": "30px",
                                            "fontFamily": "GildaDisplay",
                                        },
                                    ),
                                    html.H5(
                                        id="prod_page_subcategory",
                                        # style={'border': 'solid 1px',
                                        #        'border-color': 'lightgrey'},
                                        className="mini_container",
                                    ),
                                ],
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Img(
                                                                id="prod_page_product_image",
                                                                width=300,
                                                                height=250,
                                                                alt="Product image will be displayed here once available.",
                                                            ),
                                                            html.P(
                                                                id="prod_page_card_brand_name",
                                                                style={
                                                                    "fontSize": "16px"
                                                                },
                                                            ),
                                                            html.P(
                                                                id="prod_page_card_product_name",
                                                                style={
                                                                    "fontSize": "16px"
                                                                },
                                                            ),
                                                        ],
                                                        width=7,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            html.P(
                                                                                id="prod_page_product_review_count",
                                                                                className="mini_container",
                                                                                style={
                                                                                    "fontSize": "14.5px"
                                                                                },
                                                                            ),
                                                                        ],
                                                                        # width=4
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            html.P(
                                                                                id="prod_page_product_adjusted_rating",
                                                                                className="mini_container",
                                                                                style={
                                                                                    "fontSize": "14.5px"
                                                                                },
                                                                            ),
                                                                        ],
                                                                        # width=4
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            html.P(
                                                                                id="prod_page_product_first_review_date",
                                                                                className="mini_container",
                                                                                style={
                                                                                    "fontSize": "14.5px"
                                                                                },
                                                                            ),
                                                                        ],
                                                                        # width=4
                                                                    )
                                                                ]
                                                            ),
                                                        ],
                                                        width=5,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ],
                                # color="dark",   # https://bootswatch.com/default/ for more card colors
                                # # change color of text (black or white)
                                # inverse=True,
                                outline=False,  # True = remove the block colors from the background and header
                                style={
                                    "height": "100%",
                                },
                            )
                        ],
                        width=6,
                    ),
                ],
                className="row pretty_container",
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "normal",
                },
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="Review Analytics",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "Positive Review Summary",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P(
                                                        id="pos_review_sum",
                                                        children=[
                                                            "Here Goes Review Summary"
                                                        ],
                                                        style={
                                                            "fontName": "Calibri",
                                                            "fontSize": "15px",
                                                        },
                                                        className="mini-container",
                                                    ),
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
                                                        "Negative Review Summary",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P(
                                                        id="neg_review_sum",
                                                        children=[
                                                            "Here Goes Review Summary"
                                                        ],
                                                        style={
                                                            "fontName": "Calibri",
                                                            "fontSize": "15px",
                                                        },
                                                        className="mini-container",
                                                    ),
                                                ],
                                            )
                                        ],
                                        width=6,
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H5(
                                                "Review Overview",
                                                style={
                                                    "margin-left": "10px",
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            ),
                                        ]
                                    )
                                ],
                                className="mini-container",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    html.H6(
                                                        style={
                                                            "fontFamily": "GildaDisplay"
                                                        }
                                                    ),
                                                    dcc.Graph(
                                                        id="review_sentiment_breakdown"
                                                    ),
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Graph(
                                                        id="review_influenced_breakdown"
                                                    ),
                                                ]
                                            ),
                                        ],
                                        width=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Graph(
                                                        id="review_sentiment_timeseries"
                                                    ),
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Graph(
                                                        id="review_influenced_timeseries"
                                                    ),
                                                ]
                                            ),
                                        ],
                                        width={"size": 8, "offset": 1},
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                            dbc.Row(
                                [
                                    dbc.Row(
                                        html.H5(
                                            "Review Keyphrases",
                                            style={
                                                "margin-left": "10px",
                                                "fontFamily": "GildaDisplay",
                                            },
                                        )
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="pos_talking_points_fig"
                                                    )
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="neg_talking_points_fig"
                                                    )
                                                ],
                                                width=6,
                                            ),
                                        ]
                                    ),
                                ],
                                className="row pretty_container",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                },
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H3(
                                                "Review Distribution by User Attributes",
                                                style={
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H5(
                                                                "User Attribute:",
                                                                style={
                                                                    "fontFamily": "GildaDisplay"
                                                                },
                                                            )
                                                        ],
                                                        width=5,
                                                    ),
                                                    dbc.Col(
                                                        dcc.Dropdown(
                                                            id="prod_page_user_attribute",
                                                            options=prod_page_user_attribute_options,
                                                            multi=False,
                                                            value="age",
                                                            style={"fontSize": 14},
                                                            placeholder="Select User Attribute",
                                                            clearable=False,
                                                        ),
                                                    ),
                                                ],
                                            ),
                                            # # html.Hr(),
                                            dcc.Graph(
                                                id="prod_page_reviews_by_attribute"
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "flexDirection": "column",
                                        },
                                    ),
                                    dbc.Col(
                                        [
                                            html.H3(
                                                "Review Distribution by Stars",
                                                style={
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            ),
                                            html.Div(),
                                            dcc.Graph(id="prod_page_reviews_by_stars"),
                                        ],
                                        style={
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "justifyContent": "space-between",
                                        },
                                    ),
                                ],
                                className="pretty_container",
                            ),
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Price & Ingredient Analytics",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.H5(
                                                                        "Price Overview",
                                                                        style={
                                                                            "paddingRight": "30px",
                                                                            "fontFamily": "GildaDisplay",
                                                                        },
                                                                    )
                                                                ]
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.H5(
                                                                                id="prod_small_price_text",
                                                                                style={
                                                                                    "fontFamily": "GildaDisplay"
                                                                                },
                                                                            ),
                                                                            html.P(
                                                                                "Small Size Price"
                                                                            ),
                                                                        ],
                                                                        id="prod_min_price",
                                                                        className="mini_container",
                                                                    ),
                                                                    html.Div(
                                                                        [
                                                                            html.H5(
                                                                                id="prod_big_price_text",
                                                                                style={
                                                                                    "fontFamily": "GildaDisplay"
                                                                                },
                                                                            ),
                                                                            html.P(
                                                                                "Big Size Price"
                                                                            ),
                                                                        ],
                                                                        id="prod_max_price",
                                                                        className="mini_container",
                                                                    ),
                                                                    # html.Div(
                                                                    #     [
                                                                    #         html.H5(
                                                                    #             id="prod_mrp_text",
                                                                    #             style={
                                                                    #                 "fontFamily": "GildaDisplay"
                                                                    #             },
                                                                    #         ),
                                                                    #         html.P(
                                                                    #             "MRP"
                                                                    #         ),
                                                                    #     ],
                                                                    #     id="prod_mrp",
                                                                    #     className="mini_container",
                                                                    # ),
                                                                ],
                                                                id="info-container",
                                                                className="container-display",
                                                            ),
                                                        ],
                                                    )
                                                ]
                                            ),
                                            # html.Hr(),
                                            dbc.Row(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.H5(
                                                                        "Product Overview",
                                                                        style={
                                                                            "paddingRight": "30px",
                                                                            "fontFamily": "GildaDisplay",
                                                                        },
                                                                    )
                                                                ]
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.H5(
                                                                                id="prod_new_flag",
                                                                                style={
                                                                                    "fontFamily": "GildaDisplay"
                                                                                },
                                                                            ),
                                                                            html.P(
                                                                                "Status"
                                                                            ),
                                                                        ],
                                                                        id="prod_status",
                                                                        className="mini_container",
                                                                    ),
                                                                    html.Div(
                                                                        [
                                                                            html.H5(
                                                                                id="prod_dist_ing",
                                                                                style={
                                                                                    "fontFamily": "GildaDisplay"
                                                                                },
                                                                            ),
                                                                            html.P(
                                                                                "Distinct Ingredients"
                                                                            ),
                                                                        ],
                                                                        id="prod_ing",
                                                                        className="mini_container",
                                                                    ),
                                                                ],
                                                                id="info-container",
                                                                className="container-display",
                                                            ),
                                                        ],
                                                    )
                                                ]
                                            ),
                                        ],
                                        width=4,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Div(
                                                dcc.Graph("prod_page_price_variation"),
                                                style={"overflowY": "scroll"},
                                            )
                                        ]
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "Product Variants by Size/Color",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    )
                                                ]
                                            ),
                                            # html.Hr(),
                                            dash_table.DataTable(
                                                id="prod_page_product_variants",
                                                columns=[
                                                    {
                                                        "name": i,
                                                        "id": i,
                                                        "deletable": False,
                                                        "selectable": True,
                                                        "hideable": False,
                                                    }
                                                    for i in prod_page_item_df.columns
                                                ],
                                                # data=new_products_detail_df.to_dict(
                                                #     'records'),  # the contents of the table
                                                editable=False,  # allow editing of data inside all cells
                                                # allow filtering of data by user ('native') or not ('none')
                                                filter_action="native",
                                                # enables data to be sorted per-column by user or not ('none')
                                                sort_action="native",
                                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                                # choose if user can delete a row (True) or not (False)
                                                row_deletable=False,
                                                selected_columns=[],  # ids of columns that user selects
                                                selected_rows=[],  # indices of rows that user selects
                                                # all data is passed to the table up-front or not ('none')
                                                page_action="none",
                                                page_current=0,  # page number that user is on
                                                page_size=10,  # number of rows visible per page
                                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                                    "minWidth": 80,
                                                    "maxWidth": 80,
                                                    "width": 80,
                                                    "fontSize": 13,
                                                    "font-family": "GothamLight",
                                                },
                                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                                    {
                                                        "if": {
                                                            "column_id": "product_name"
                                                        },
                                                        "textAlign": "left",
                                                        "minWidth": 120,
                                                        "maxWidth": 160,
                                                        "width": 160,
                                                    },
                                                    {
                                                        "if": {
                                                            "column_id": "item_name"
                                                        },
                                                        "textAlign": "left",
                                                        "minWidth": 120,
                                                        "maxWidth": 120,
                                                        "width": 120,
                                                    },
                                                    {
                                                        "if": {
                                                            "column_id": "item_size"
                                                        },
                                                        "textAlign": "left",
                                                    },
                                                ],
                                                style_data={  # overflow cells' content into multiple lines
                                                    "whiteSpace": "normal",
                                                    "height": "auto",
                                                },
                                                fixed_rows={"headers": True},
                                                style_table={"overflow": "auto"},
                                            ),
                                        ],
                                        width=12,
                                        className="pretty_container",
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "Product Ingredients",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    )
                                                ]
                                            ),
                                            # html.Hr(),
                                            dash_table.DataTable(
                                                id="prod_page_ingredients",
                                                columns=[
                                                    {
                                                        "name": i,
                                                        "id": i,
                                                        "deletable": False,
                                                        "selectable": True,
                                                        "hideable": False,
                                                    }
                                                    for i in [
                                                        "ingredient",
                                                        "ingredient_type",
                                                        "ban_flag",
                                                        "new_flag",
                                                    ]
                                                ],
                                                # data=new_products_detail_df.to_dict(
                                                #     'records'),  # the contents of the table
                                                editable=False,  # allow editing of data inside all cells
                                                # allow filtering of data by user ('native') or not ('none')
                                                filter_action="native",
                                                # enables data to be sorted per-column by user or not ('none')
                                                sort_action="native",
                                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                                # choose if user can delete a row (True) or not (False)
                                                row_deletable=False,
                                                selected_columns=[],  # ids of columns that user selects
                                                selected_rows=[],  # indices of rows that user selects
                                                # all data is passed to the table up-front or not ('none')
                                                page_action="none",
                                                # page_current=0,  # page number that user is on
                                                # page_size=15,  # number of rows visible per page
                                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                                    "minWidth": 80,
                                                    "maxWidth": 80,
                                                    "width": 80,
                                                    "fontSize": 13,
                                                    "font-family": "GothamLight",
                                                },
                                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                                    {
                                                        "if": {
                                                            "column_id": "ingredient"
                                                        },
                                                        "textAlign": "left",
                                                        "minWidth": 120,
                                                        "maxWidth": 160,
                                                        "width": 160,
                                                    },
                                                    {
                                                        "if": {
                                                            "column_id": "ingredient_type"
                                                        },
                                                        "textAlign": "left",
                                                        "minWidth": 120,
                                                        "maxWidth": 120,
                                                        "width": 120,
                                                    },
                                                    {
                                                        "if": {
                                                            "column_id": "item_size"
                                                        },
                                                        "textAlign": "left",
                                                    },
                                                ],
                                                style_data={  # overflow cells' content into multiple lines
                                                    "whiteSpace": "normal",
                                                    "height": "auto",
                                                },
                                                fixed_rows={"headers": True},
                                                style_table={
                                                    "height": 500,
                                                    "overflow": "auto",
                                                },
                                            ),
                                        ],
                                        width=12,
                                        className="pretty_container",
                                    ),
                                ],
                                className="row pretty_container",
                            ),
                        ],
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                ],
                style=tabs_styles,
                colors={
                    "border": "white",
                    "primary": "gold",
                    "background": "cornsilk",
                },
            ),
        ],
        id="mainContainer",
        style={
            "fontFamily": "GothamLight",
            "display": "flex",
            "flex-direction": "column",
            "overflow": "scroll",
        },
    )


def ingredient_page_layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H2(
                            "Ingredient Search and Analysis",
                            style={
                                "color": "black",
                                #    'border': '0.5px grey dotted',
                                "width": "auto",
                                "fontFamily": "GildaDisplay",
                            },
                            className="row pretty_container",
                        )
                    )
                ]
            ),
            html.Div(
                [
                    html.H3(
                        "Find Products by Ingredient",
                        style={
                            "fontFamily": "GildaDisplay",
                        },
                    ),
                    # # html.Hr(),
                    html.Div(
                        [
                            html.H4(
                                "Search Ingredient",
                                style={
                                    "fontFamily": "GildaDisplay",
                                },
                            ),
                            dcc.Dropdown(
                                id="ing_page_ing",
                                options=ing_page_ingredient_options,
                                multi=False,
                                style={"fontSize": 14},
                                placeholder="Select Ingredient",
                                clearable=False,
                            ),
                        ],
                        style={"width": "60%"},
                        className="pretty_container",
                    ),
                    dbc.Row(
                        [
                            dbc.Col([dcc.Graph(id="ing_page_ing_cat_presence")]),
                            dbc.Col(
                                [
                                    dbc.Row([html.H5(id="ing_page_click_data_text")]),
                                    html.Div(
                                        dcc.Graph(id="ing_page_ing_subcat_presence"),
                                        style={"overflowX": "scroll", "width": 1000},
                                    ),
                                ]
                            ),
                        ],
                        className="pretty_container",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dash_table.DataTable(
                                        id="ing_page_prod_search_table",
                                        columns=[
                                            {
                                                "name": i,
                                                "id": i,
                                                "deletable": False,
                                                "selectable": True,
                                                "hideable": False,
                                            }
                                            for i in [
                                                "product_name",
                                                "product_type",
                                                "category",
                                                "source",
                                            ]
                                        ],
                                        # data=new_products_detail_df.to_dict(
                                        #     'records'),  # the contents of the table
                                        editable=False,  # allow editing of data inside all cells
                                        # allow filtering of data by user ('native') or not ('none')
                                        filter_action="native",
                                        # enables data to be sorted per-column by user or not ('none')
                                        sort_action="native",
                                        sort_mode="single",  # sort across 'multi' or 'single' columns
                                        # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                        # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                        # choose if user can delete a row (True) or not (False)
                                        row_deletable=False,
                                        selected_columns=[],  # ids of columns that user selects
                                        selected_rows=[],  # indices of rows that user selects
                                        # all data is passed to the table up-front or not ('none')
                                        page_action="native",
                                        # page_current=0,  # page number that user is on
                                        # page_size=0,  # number of rows visible per page
                                        style_cell={  # ensure adequate header width when text is shorter than cell's text
                                            "minWidth": 80,
                                            "maxWidth": 80,
                                            "width": 80,
                                            "fontSize": 13,
                                            "font-family": "GothamLight",
                                            "textAlign": "left",
                                        },
                                        style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                            {
                                                "if": {"column_id": "product_name"},
                                                "minWidth": 120,
                                                "maxWidth": 160,
                                                "width": 160,
                                            },
                                            {
                                                "if": {"column_id": "product_type"},
                                                "textAlign": "left",
                                                "minWidth": 120,
                                                "maxWidth": 120,
                                                "width": 120,
                                            },
                                        ],
                                        style_data={  # overflow cells' content into multiple lines
                                            "whiteSpace": "normal",
                                            "height": "auto",
                                        },
                                        fixed_rows={"headers": True},
                                        style_table={
                                            "overflow": "auto",
                                        },
                                    )
                                ],
                                width=12,
                            ),
                        ],
                        className="pretty_container",
                    ),
                ],
                className="pretty_container",
            ),
            dbc.Row(
                html.H4(
                    "Ingredient Analysis by Category/Subcategory",
                    style={
                        "fontFamily": "GildaDisplay",
                    },
                ),
                className="mini_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(
                                    "Geography",
                                    style={
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="ing_page_source",
                                    options=ing_page_source_options,
                                    multi=False,
                                    value="us",
                                    style={"fontSize": 14},
                                    placeholder="Select Geography",
                                    clearable=False,
                                ),
                            ],
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(
                                    "Category",
                                    style={
                                        "paddingRight": "30px",
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="ing_page_category",
                                    options=ing_page_category_options,
                                    multi=False,
                                    style={"fontSize": 14, "width": "100%"},
                                    placeholder="Select Category",
                                    value="skincare",
                                    clearable=False,
                                ),
                            ],
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(
                                    "Subcategory",
                                    style={
                                        "paddingRight": "30px",
                                        "fontFamily": "GildaDisplay",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="ing_page_product_type",
                                    options=ing_page_product_type_options,
                                    multi=False,
                                    style={"fontSize": 14, "width": "100%"},
                                    placeholder="Select Subcategory",
                                ),
                            ],
                        ),
                        width=5,
                    ),
                ],
                className="row pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H4(
                                                "Ingredient Analysis",
                                                style={
                                                    "paddingRight": "30px",
                                                    "fontFamily": "GildaDisplay",
                                                },
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="new_ing_count_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("New Ingredients"),
                                                ],
                                                id="new_ing",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="distinct_ing_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P("Distinct Ingredients"),
                                                ],
                                                id="distinct_ing",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [
                                                    html.H5(
                                                        id="banned_ing_text",
                                                        style={
                                                            "fontFamily": "GildaDisplay",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Distinct Banned Ingredients"
                                                    ),
                                                ],
                                                id="banned_ing",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="info-container",
                                        className="container-display",
                                    ),
                                ],
                            )
                        ],
                        width=5,
                    ),
                    dbc.Col([html.Div(dcc.Graph("ing_page_ing_type_fig"))], width=7),
                ],
                className="pretty_container",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6(
                                "Banned Ingredients",
                                style={"fontFamily": "GildaDisplay"},
                            ),
                            dash_table.DataTable(
                                id="ing_page_banned_ing_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in ["ingredient", "product_name"]
                                ],
                                # data=new_products_detail_df.to_dict(
                                #     'records'),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="none",
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 80,
                                    "maxWidth": 80,
                                    "width": 80,
                                    "fontSize": 13,
                                    "font-family": "GothamLight",
                                    "textAlign": "left",
                                },
                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                    {
                                        "if": {"column_id": "product_name"},
                                        "minWidth": 120,
                                        "maxWidth": 150,
                                        "width": 150,
                                    },
                                    {
                                        "if": {"column_id": "ingredient"},
                                        "minWidth": 120,
                                        "maxWidth": 120,
                                        "width": 120,
                                    },
                                ],
                                style_data={  # overflow cells' content into multiple lines
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                fixed_rows={"headers": True},
                                style_table={
                                    "overflow": "auto",
                                },
                            ),
                        ],
                        width=5,
                    ),
                    dbc.Col(
                        [
                            html.H6(
                                "New Ingredients",
                                style={"fontFamily": "GildaDisplay"},
                            ),
                            dash_table.DataTable(
                                id="ing_page_new_ing_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        "deletable": False,
                                        "selectable": True,
                                        "hideable": False,
                                    }
                                    for i in [
                                        "ingredient",
                                        "ingredient_type",
                                        "product_name",
                                    ]
                                ],
                                # data=new_products_detail_df.to_dict(
                                #     'records'),  # the contents of the table
                                editable=False,  # allow editing of data inside all cells
                                # allow filtering of data by user ('native') or not ('none')
                                filter_action="native",
                                # enables data to be sorted per-column by user or not ('none')
                                sort_action="native",
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                # row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                                # choose if user can delete a row (True) or not (False)
                                row_deletable=False,
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                # all data is passed to the table up-front or not ('none')
                                page_action="none",
                                style_cell={  # ensure adequate header width when text is shorter than cell's text
                                    "minWidth": 60,
                                    "maxWidth": 60,
                                    "width": 60,
                                    "fontSize": 13,
                                    "font-family": "GothamLight",
                                    "textAlign": "left",
                                },
                                style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                                    {
                                        "if": {"column_id": "product_name"},
                                        "minWidth": 120,
                                        "maxWidth": 150,
                                        "width": 150,
                                    },
                                    {
                                        "if": {"column_id": "ingredient"},
                                        "minWidth": 120,
                                        "maxWidth": 120,
                                        "width": 120,
                                    },
                                ],
                                style_data={  # overflow cells' content into multiple lines
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                fixed_rows={"headers": True},
                                style_table={
                                    "overflow": "auto",
                                },
                            ),
                        ],
                        width=7,
                    ),
                ],
                className="pretty_container",
            ),
        ],
        id="mainContainer",
        style={
            "fontFamily": "GothamLight",
            "display": "flex",
            "flex-direction": "column",
        },
    )


def mark_digit(d):
    return format(d, ",d")


# Ingredient Page Callbacks


@app.callback(
    Output("ing_page_click_data_text", "children"),
    [
        Input("ing_page_ing_cat_presence", "clickData"),
    ],
)
def display_click_data_ing_page(clickData) -> str:
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
        return "Click on the bar of a Category to display ingredient distribution over Subcategories under it."


@app.callback(
    Output("ing_page_ing_subcat_presence", "figure"),
    [Input("ing_page_ing", "value"), Input("ing_page_ing_cat_presence", "clickData")],
)
def update_ing_page_category_count_figure(ingredient: str, clickData):
    """update_ing_page_category_count_figure [summary]

    [extended_summary]

    Args:
        ingredient (str): [description]

    Returns:
        [type]: [description]
    """
    if clickData is not None:
        category = clickData["points"][0]["customdata"][0]

        data = (
            ing_page_ing_df[
                (ing_page_ing_df.category == category)
                & (ing_page_ing_df.ingredient == ingredient)
            ][["product_name", "product_type"]]
            .groupby(by=["product_type"])
            .product_name.size()
            .reset_index()
        )
        data.columns = ["product_type", "product_count"]
        data.category = data.product_type.astype(str)

        fig = create_ing_page_category_count_figure(
            data, "product_type", ingredient, orientation="v"
        )

        return fig
    return {}


@app.callback(
    Output("ing_page_ing_cat_presence", "figure"), [Input("ing_page_ing", "value")]
)
def update_ing_page_category_count_figure(ingredient: str):
    """update_ing_page_category_count_figure [summary]

    [extended_summary]

    Args:
        ingredient (str): [description]

    Returns:
        [type]: [description]
    """
    if ingredient:
        data = (
            ing_page_ing_df[["product_name", "category"]][
                ing_page_ing_df.ingredient == ingredient
            ]
            .groupby(by=["category"])
            .product_name.size()
            .reset_index()
        )
        data.columns = ["category", "product_count"]
        data.category = data.category.astype(str)

        fig = create_ing_page_category_count_figure(data, "category", ingredient)

        return fig
    return {}


@app.callback(
    Output("ing_page_new_ing_table", "data"),
    [
        Input("ing_page_source", "value"),
        Input("ing_page_category", "value"),
        Input("ing_page_product_type", "value"),
    ],
)
def update_ing_page_new_ing_table(
    source: str, category: str, product_type: str
) -> list:
    """update_ing_page_new_ing_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        list: [description]
    """
    new_ing = prod_page_ing_df[prod_page_ing_df.new_flag == "new_ingredient"][
        (prod_page_ing_df.source == source)
        & (prod_page_ing_df.category == category)
        & (prod_page_ing_df.product_type == product_type)
    ][["ingredient", "ingredient_type", "product_name"]]
    for col in new_ing.columns:
        new_ing[col] = new_ing[col].astype(str)
    new_ing = (
        new_ing.groupby(by=["ingredient", "ingredient_type"])
        .product_name.apply(", ".join)
        .reset_index()
    )

    return new_ing.to_dict("records")


@app.callback(
    Output("ing_page_banned_ing_table", "data"),
    [
        Input("ing_page_source", "value"),
        Input("ing_page_category", "value"),
        Input("ing_page_product_type", "value"),
    ],
)
def update_ing_page_banned_ing_table(
    source: str, category: str, product_type: str
) -> list:
    """update_ing_page_banned_ing_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        list: [description]
    """
    ban_ing = ing_page_ing_df[ing_page_ing_df.ban_flag == "yes"][
        (ing_page_ing_df.source == source)
        & (ing_page_ing_df.category == category)
        & (ing_page_ing_df.product_type == product_type)
    ][["ingredient", "product_name"]].drop_duplicates()
    ban_ing.product_name = ban_ing.product_name.astype("str")
    ban_ing.reset_index(inplace=True, drop=True)
    ban_ing = ban_ing.groupby("product_name").ingredient.apply(", ".join).reset_index()

    return ban_ing.to_dict("records")


@app.callback(
    Output("ing_page_prod_search_table", "data"),
    [Input("ing_page_ing", "value")],
)
def update_ing_page_product_table(ingredient: str) -> list:
    """update_ing_page_product_table [summary]

    [extended_summary]

    Args:
        ingredient (str): [description]

    Returns:
        list: [description]
    """
    data = (
        ing_page_ing_df[["product_name", "product_type", "category", "source"]][
            ing_page_ing_df.ingredient == ingredient
        ]
        .drop_duplicates()
        .sort_values("source", ascending=False)
    )
    return data.to_dict("records")


@app.callback(
    Output("ing_page_ing_type_fig", "figure"),
    [
        Input("ing_page_source", "value"),
        Input("ing_page_category", "value"),
        Input("ing_page_product_type", "value"),
    ],
)
def update_ing_page_ingredient_type_figure(
    source: str, category: str, product_type: str
) -> go.Figure:
    from bte_ingredient_page_data_and_plots import (
        create_ing_page_ingredient_type_figure,
    )

    fig = create_ing_page_ingredient_type_figure(source, category, product_type)
    return fig


@app.callback(
    [
        Output("new_ing_count_text", "children"),
        Output("distinct_ing_text", "children"),
        Output("banned_ing_text", "children"),
    ],
    [
        Input("ing_page_source", "value"),
        Input("ing_page_category", "value"),
        Input("ing_page_product_type", "value"),
    ],
)
def update_ing_page_ing_analysis_text(
    source: str, category: str, product_type: str
) -> Tuple[str, str, str, str]:
    """update_text [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        Tuple[str, str, str, str]: [description]
    """
    new_ing = prod_page_ing_df[prod_page_ing_df.new_flag == "new_ingredient"][
        (prod_page_ing_df.source == source)
        & (prod_page_ing_df.category == category)
        & (prod_page_ing_df.product_type == product_type)
    ].ingredient.nunique()

    dist_ing = ing_page_ing_df[
        (ing_page_ing_df.source == source)
        & (ing_page_ing_df.category == category)
        & (ing_page_ing_df.product_type == product_type)
    ].ingredient.nunique()

    ban_ing = ing_page_ing_df[ing_page_ing_df.ban_flag == "yes"][
        (ing_page_ing_df.source == source)
        & (ing_page_ing_df.category == category)
        & (ing_page_ing_df.product_type == product_type)
    ].ingredient.nunique()

    return new_ing, dist_ing, ban_ing


@app.callback(
    Output("ing_page_product_type", "options"),
    [Input("ing_page_source", "value"), Input("ing_page_category", "value")],
)
def set_ing_page_product_type_options(source: str, category: str):
    return [
        {"label": i, "value": i}
        for i in ing_page_ing_df.product_type[
            (ing_page_ing_df.source == source) & (ing_page_ing_df.category == category)
        ]
        .unique()
        .tolist()
    ]


@app.callback(
    Output("ing_page_product_type", "value"),
    [
        Input("ing_page_source", "value"),
        Input("ing_page_category", "value"),
        Input("ing_page_product_type", "options"),
    ],
)
def set_ing_page_product_type_value(source, category, available_options):
    return available_options[0]["value"]


# Product Page Callbacks
@app.callback(
    Output("prod_page_ingredients", "data"),
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
    ],
)
def update_prod_page_product_ingredients_table(source: str, prod_id: str) -> list:
    """update_prod_page_product_ingredients_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        prod_id (str): [description]

    Returns:
        list: [description]
    """
    data = prod_page_ing_df[["ingredient", "ingredient_type", "ban_flag", "new_flag"]][
        prod_page_ing_df.prod_id == prod_id
    ]

    data.sort_values(by="ingredient", inplace=True, ascending=True)

    return data.to_dict("records")


@app.callback(
    Output("prod_page_product_variants", "data"),
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def update_prod_page_product_variants_table(
    source: str, prod_id: str, start_date: str, end_date: str
) -> list:
    """update_prod_page_product_variants_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        prod_id (str): [description]
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        list: [description]
    """
    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    data = prod_page_item_df[
        (prod_page_item_df.prod_id == prod_id)
        & (prod_page_item_df.meta_date >= start_date_string)
        & (prod_page_item_df.meta_date <= end_date_string)
    ]
    data = data[(data.meta_date == data[data.prod_id == prod_id].meta_date.max())]

    data.sort_values(by="item_size", inplace=True, ascending=False)

    return data.to_dict("records")


@app.callback(
    Output("prod_page_price_variation", "figure"),
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def update_prod_page_item_price_figure(
    source: str, prod_id: str, start_date: str, end_date: str
) -> go.Figure:
    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    data = prod_page_item_price_df[
        (prod_page_item_price_df.prod_id == prod_id)
        & (prod_page_item_price_df.meta_date >= start_date_string)
        & (prod_page_item_price_df.meta_date <= end_date_string)
    ]

    fig = create_prod_page_item_price_figure(data)

    return fig


@app.callback(
    [
        Output("prod_small_price_text", "children"),
        Output("prod_big_price_text", "children"),
        # Output("prod_mrp_text", "children"),
        Output("prod_new_flag", "children"),
        Output("prod_dist_ing", "children"),
    ],
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
    ],
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
    prices = prod_page_item_price_df[
        (
            prod_page_item_price_df.meta_date
            == prod_page_item_price_df[
                prod_page_item_price_df.source == source
            ].meta_date.max()
        )
        & (prod_page_item_price_df.source == source)
        & (prod_page_item_price_df.prod_id == prod_id)
    ].item_price.tolist()

    status = prod_page_metadetail_data_df.new_flag[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]

    dist_ing = prod_page_ing_df[
        prod_page_ing_df.prod_id == prod_id
    ].ingredient.nunique()

    if source == "us":
        currency = "$"
    else:
        currency = "£"

    return (
        f"{currency}{min(prices)}",
        f"{currency}{max(prices)}",
        status.title(),
        dist_ing,
    )


@app.callback(
    Output("prod_page_reviews_by_stars", "figure"),
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def update_prod_page_reviews_distribution_figure(
    source: str, prod_id: str, start_date: str, end_date: str
) -> Tuple[go.Figure, go.Figure]:
    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string)
        & (prod_page_review_sentiment_influence_df.review_date <= end_date_string)
    ]

    star_fig = create_prod_page_reviews_distribution_figure(data=data, prod_id=prod_id)
    return star_fig


@app.callback(
    Output("prod_page_reviews_by_attribute", "figure"),
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_user_attribute", "value"),
    ],
)
def update_prod_page_reviews_by_user_attribute_figure(
    source: str, prod_id: str, user_attribute: str
) -> go.Figure:
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
        prod_id=prod_id, user_attribute=user_attribute
    )
    return fig


@app.callback(
    dash.dependencies.Output(
        "prod-page-output-container-date-picker-range", "children"
    ),
    [
        dash.dependencies.Input("prod_page_review_month_range", "start_date"),
        dash.dependencies.Input("prod_page_review_month_range", "end_date"),
    ],
)
def date_selection_text(start_date: str, end_date: str) -> str:
    """date_selection_text [summary]

    [extended_summary]

    Args:
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        str: [description]
    """
    return "Minimum start date is 12/01/2008. \n You can write in MM/DD/YYYY format in the date box to filter."


@app.callback(
    [
        Output("review_sentiment_timeseries", "figure"),
        Output("review_influenced_timeseries", "figure"),
    ],
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def update_prod_page_review_timeseries_figure(
    source: str, prod_id: str, start_date: str, end_date: str
) -> Tuple[go.Figure, go.Figure]:
    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string)
        & (prod_page_review_sentiment_influence_df.review_date <= end_date_string)
    ]

    sent_fig = create_prod_page_review_timeseries_figure(data, prod_id, "sentiment")
    inf_fig = create_prod_page_review_timeseries_figure(data, prod_id, "is_influenced")
    return sent_fig, inf_fig


@app.callback(
    [
        Output("review_sentiment_breakdown", "figure"),
        Output("review_influenced_breakdown", "figure"),
    ],
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def update_prod_page_review_breakdown_figure(
    source: str, prod_id: str, start_date: str, end_date: str
) -> Tuple[go.Figure, go.Figure]:
    from bte_product_page_data_and_plots import (
        create_prod_page_review_breakdown_figure,
        prod_page_review_sentiment_influence_df,
    )

    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    data = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.review_date >= start_date_string)
        & (prod_page_review_sentiment_influence_df.review_date <= end_date_string)
    ]

    sent_fig = create_prod_page_review_breakdown_figure(data, prod_id, "sentiment")
    inf_fig = create_prod_page_review_breakdown_figure(data, prod_id, "is_influenced")
    return sent_fig, inf_fig


@app.callback(
    [
        Output("pos_talking_points_fig", "figure"),
        Output("neg_talking_points_fig", "figure"),
    ],
    [Input("prod_page_source", "value"), Input("prod_page_product", "value")],
)
def update_prod_page_review_talking_points_figure(source: str, prod_id: str):
    from bte_product_page_data_and_plots import (
        create_prod_page_review_talking_points_figure,
        prod_page_review_talking_points_df,
    )

    pos_fig = create_prod_page_review_talking_points_figure(
        prod_page_review_talking_points_df, prod_id, "pos_talking_points"
    )
    neg_fig = create_prod_page_review_talking_points_figure(
        prod_page_review_talking_points_df, prod_id, "neg_talking_points"
    )
    return pos_fig, neg_fig


@app.callback(
    [
        Output("pos_review_sum", "children"),
        Output("neg_review_sum", "children"),
    ],
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
    ],
)
def display_product_page_category(source: str, prod_id: str):
    if (
        len(
            prod_page_review_sum_df.pos_review_summary[
                prod_page_review_sum_df.prod_id == prod_id
            ]
        )
        > 0
    ):
        pos_sum = prod_page_review_sum_df.pos_review_summary[
            prod_page_review_sum_df.prod_id == prod_id
        ].values[0]
    else:
        pos_sum = ""
    if (
        len(
            prod_page_review_sum_df.neg_review_summary[
                prod_page_review_sum_df.prod_id == prod_id
            ]
        )
        > 0
    ):
        neg_sum = prod_page_review_sum_df.neg_review_summary[
            prod_page_review_sum_df.prod_id == prod_id
        ].values[0]
    else:
        neg_sum = ""
    return pos_sum, neg_sum


@app.callback(
    Output("prod_page_product_image", "src"),
    [Input("prod_page_source", "value"), Input("prod_page_product", "value")],
)
def update_prod_page_img_src(source: str, prod_id: str):
    # commented by Arnold #
    # return image URL strictly from read_image_s3 #
    # prod_img_path = read_image_s3(prod_id=prod_id)
    # encoded_image = base64.b64encode(open(prod_img_path, 'rb').read())
    # return 'data:image/png;base64,{}'.format(encoded_image.decode())
    return read_image_s3(prod_id=prod_id)


@app.callback(
    [
        Output("prod_page_card_brand_name", "children"),
        Output("prod_page_card_product_name", "children"),
        Output("prod_page_product_review_count", "children"),
        Output("prod_page_product_adjusted_rating", "children"),
        Output("prod_page_product_first_review_date", "children"),
    ],
    [
        Input("prod_page_source", "value"),
        Input("prod_page_product", "value"),
        Input("prod_page_review_month_range", "start_date"),
        Input("prod_page_review_month_range", "end_date"),
    ],
)
def display_product_data_in_card(
    source: str, prod_id: str, start_date: str, end_date: str
):
    if start_date is not None:
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date
    prod_name = prod_page_metadetail_data_df.product_name[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    brand_name = prod_page_metadetail_data_df.brand[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    reviews = prod_page_review_sentiment_influence_df[
        (prod_page_review_sentiment_influence_df.prod_id == prod_id)
        & (prod_page_review_sentiment_influence_df.review_date >= start_date_string)
        & (prod_page_review_sentiment_influence_df.review_date <= end_date_string)
    ].shape[0]
    adjusted_rating = prod_page_metadetail_data_df.adjusted_rating[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    first_review_date = prod_page_metadetail_data_df.first_review_date[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    return (
        f"Brand: {brand_name}",
        f"Product Name: {prod_name}",
        f"Product Reviews: {reviews}",
        f"Product Rating: {adjusted_rating}",
        f"First Review Date: {first_review_date}",
    )


@app.callback(
    [
        Output("prod_page_category", "children"),
        Output("prod_page_subcategory", "children"),
    ],
    [Input("prod_page_source", "value"), Input("prod_page_product", "value")],
)
def display_product_page_category(source: str, prod_id: str):
    category = prod_page_metadetail_data_df.category[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    product_type = prod_page_metadetail_data_df.product_type[
        (prod_page_metadetail_data_df.source == source)
        & (prod_page_metadetail_data_df.prod_id == prod_id)
    ].values[0]
    return category, product_type


@app.callback(
    Output("prod_page_product", "options"), [Input("prod_page_source", "value")]
)
def set_product_page_product_options(source: str):
    return sorted(
        [
            {"label": i[0], "value": i[1]}
            for i in prod_page_metadetail_data_df[["product_name", "prod_id"]][
                prod_page_metadetail_data_df.source == source
            ].values.tolist()
        ],
        key=lambda k: k["label"],
    )


@app.callback(
    Output("prod_page_product", "value"),
    [Input("prod_page_source", "value"), Input("prod_page_product", "options")],
)
def set_product_page_product_value(source, available_options):
    return available_options[10]["value"]


# Category Page Callbacks


@app.callback(
    Output("cat_page_reviews_by_attribute", "figure"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
        Input("cat_page_user_attribute", "value"),
    ],
)
def update_reviews_by_user_attribute_figure(
    source: str, category: str, product_type: str, user_attribute: str
) -> go.Figure:
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
    fig = create_reviews_by_user_attribute_figure(
        source=source,
        category=category,
        product_type=product_type,
        user_attribute=user_attribute,
    )

    return fig


@app.callback(
    Output("new_ingredients_data_table", "data"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def filter_new_ingredients_data_table(
    source: str, category: str, product_type: str
) -> pd.DataFrame:
    """filter_new_ingredients_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    new_ingredients_df = (
        cat_page_new_ingredients_df[
            (cat_page_new_ingredients_df.source == source)
            & (cat_page_new_ingredients_df.category == category)
            & (cat_page_new_ingredients_df.product_type == product_type)
        ]
        .sort_values(by="adjusted_rating", ascending=False)[
            [
                "brand",
                "product_name",
                "ingredient",
                "ingredient_type",
                "ban_flag",
            ]
        ]
        .reset_index(drop=True)
    )

    return new_ingredients_df.to_dict("records")


@app.callback(
    Output("new_products_data_table", "data"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def filter_new_products_data_table(
    source: str, category: str, product_type: str
) -> pd.DataFrame:
    """filter_new_products_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    new_products_detail_df = cat_page_new_products_details_df[
        [
            "brand",
            "product_name",
            "adjusted_rating",
            "first_review_date",
            "reviews",
            "positive_reviews",
            "negative_reviews",
        ]
    ][
        (cat_page_new_products_details_df.source == source)
        & (cat_page_new_products_details_df.category == category)
        & (cat_page_new_products_details_df.product_type == product_type)
    ]

    new_products_detail_df.sort_values(
        by="adjusted_rating", inplace=True, ascending=False
    )

    return new_products_detail_df.to_dict("records")


@app.callback(
    Output("top_products_data_table", "data"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def filter_top_products_data_table(
    source: str, category: str, product_type: str
) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    top_products_df = cat_page_top_products_df[
        [
            "brand",
            "product_name",
            "adjusted_rating",
            "first_review_date",
            "reviews",
            "positive_reviews",
            "negative_reviews",
        ]
    ][
        (cat_page_top_products_df.source == source)
        & (cat_page_top_products_df.category == category)
        & (cat_page_top_products_df.product_type == product_type)
    ]

    top_products_df.sort_values(by="adjusted_rating", inplace=True, ascending=False)

    return top_products_df.to_dict("records")


@app.callback(
    Output("product_package_data_table", "data"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def filter_product_packaging_data_table(
    source: str, category: str, product_type: str
) -> pd.DataFrame:
    """filter_product_packaging_data_table [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    packaging_filtered_df = cat_page_item_package_oz_df[
        ["item_size", "product_count", "avg_price"]
    ][
        (cat_page_item_package_oz_df.source == source)
        & (cat_page_item_package_oz_df.category == category)
        & (cat_page_item_package_oz_df.product_type == product_type)
    ]

    packaging_filtered_df.sort_values(by="product_count", inplace=True, ascending=False)

    return packaging_filtered_df.to_dict("records")


@app.callback(
    Output("cat_page_product_type", "options"),
    [Input("cat_page_source", "value"), Input("cat_page_category", "value")],
)
def set_category_page_product_type_options(source: str, category: str):
    return [
        {"label": i, "value": i}
        for i in cat_page_pricing_analytics_df.product_type[
            (cat_page_pricing_analytics_df.source == source)
            & (cat_page_pricing_analytics_df.category == category)
        ].unique()
    ]


@app.callback(
    Output("cat_page_product_type", "value"),
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "options"),
    ],
)
def set_category_page_product_type_value(source, category, available_options):
    return available_options[0]["value"]


@app.callback(
    [
        Output("distinct_brands_text", "children"),
        Output("distinct_products_text", "children"),
        Output("product_variations_text", "children"),
        Output("new_products_text", "children"),
    ],
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def update_product_analysis_text(
    source: str, category: str, product_type: str
) -> Tuple[str, str, str, str]:
    """update_text [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        Tuple[str, str, str, str]: [description]
    """
    dist_list = cat_page_distinct_brands_products_df[
        ["distinct_brands", "distinct_products"]
    ][
        (cat_page_distinct_brands_products_df.source == source)
        & (cat_page_distinct_brands_products_df.category == category)
        & (cat_page_distinct_brands_products_df.product_type == product_type)
    ].values.tolist()[
        0
    ]

    new_products_list = cat_page_new_products_count_df.new_product_count[
        (cat_page_new_products_count_df.source == source)
        & (cat_page_new_products_count_df.category == category)
        & (cat_page_new_products_count_df.product_type == product_type)
    ].values.tolist()

    product_variations = cat_page_item_variations_price_df.product_variations[
        (cat_page_item_variations_price_df.source == source)
        & (cat_page_item_variations_price_df.category == category)
        & (cat_page_item_variations_price_df.product_type == product_type)
    ].values.tolist()
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
        Output("avg_item_price_text", "children"),
    ],
    [
        Input("cat_page_source", "value"),
        Input("cat_page_category", "value"),
        Input("cat_page_product_type", "value"),
    ],
)
def update_pricing_analysis_text(
    source: str, category: str, product_type: str
) -> Tuple[str, str, str, str]:
    """update_text [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        Tuple[str, str, str, str]: [description]
    """
    pricing_data = [
        f"${p}" if source == "us" else f"£{p}"
        for p in cat_page_pricing_analytics_df[
            ["min_price", "max_price", "avg_low_price", "avg_high_price"]
        ][
            (cat_page_pricing_analytics_df.source == source)
            & (cat_page_pricing_analytics_df.category == category)
            & (cat_page_pricing_analytics_df.product_type == product_type)
        ].values.tolist()[
            0
        ]
    ]
    item_price = [
        f"${p}" if source == "us" else f"£{p}"
        for p in cat_page_item_variations_price_df.avg_item_price[
            (cat_page_item_variations_price_df.source == source)
            & (cat_page_item_variations_price_df.category == category)
            & (cat_page_item_variations_price_df.product_type == product_type)
        ].values.tolist()
    ]

    return (
        pricing_data[0],
        pricing_data[1],
        pricing_data[2],
        pricing_data[3],
        item_price[0],
    )


# Market Trend Page Callbacks
@app.callback(
    Output("category_trend", "figure"),
    inputs=[
        Input("source", "value"),
        Input("category", "value"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_category_review_trend_figure(
    source: str, category: list, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    fig = create_category_review_trend_figure(
        review_trend_category_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )

    return fig


@app.callback(
    Output("influenced_category_trend", "figure"),
    inputs=[
        Input("source", "value"),
        Input("category", "value"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_category_influenced_review_trend_figure(
    source: str, category: list, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    fig = create_category_review_trend_figure(
        influenced_review_trend_category_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
    return fig


@app.callback(
    Output("influenced_category_name", "children"),
    [
        Input("influenced_category_trend", "clickData"),
    ],
)
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
        return ""


@app.callback(
    Output("category_name", "children"),
    [
        Input("category_trend", "clickData"),
    ],
)
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
        return ""


@app.callback(
    Output("subcategory_trend", "figure"),
    [
        Input("source", "value"),
        Input("category_trend", "clickData"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_product_type_review_trend_figure(
    source: str, clickData, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    if clickData is not None:
        category = clickData["points"][0]["customdata"][0]

        # pt_df = review_trend_product_type_df[(review_trend_product_type_df.category==category)
        #                               review_trend_product_type_df.source==source]
        product_type_count = len(
            review_trend_product_type_df[
                (review_trend_product_type_df.category == category)
                & (review_trend_product_type_df.source == source)
            ].product_type.unique()
        )
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
            data=review_trend_product_type_df,
            source=source,
            category=category,
            height=height,
            start_date=start_date_string,
            end_date=end_date_string,
        )
        return fig
    else:
        return {}


@app.callback(
    Output("influenced_subcategory_trend", "figure"),
    [
        Input("source", "value"),
        Input("influenced_category_trend", "clickData"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_product_type_influenced_review_trend_figure(
    source: str, clickData, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    if clickData is not None:
        category = clickData["points"][0]["customdata"][0]

        # pt_df = review_trend_product_type_df[(review_trend_product_type_df.category==category)
        #                               review_trend_product_type_df.source==source]
        product_type_count = len(
            influenced_review_trend_product_type_df[
                (influenced_review_trend_product_type_df.category == category)
                & (influenced_review_trend_product_type_df.source == source)
            ].product_type.unique()
        )
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
            data=influenced_review_trend_product_type_df,
            source=source,
            category=category,
            height=height,
            start_date=start_date_string,
            end_date=end_date_string,
        )
        return fig
    else:
        return {}


@app.callback(
    dash.dependencies.Output("output-container-date-picker-range", "children"),
    [
        dash.dependencies.Input("review_month_range", "start_date"),
        dash.dependencies.Input("review_month_range", "end_date"),
    ],
)
def date_selection_text(start_date: str, end_date: str) -> str:
    """date_selection_text [summary]

    [extended_summary]

    Args:
        start_date (str): [description]
        end_date (str): [description]

    Returns:
        str: [description]
    """
    return "Minimum start date is 12/01/2008. \n You can write in MM/DD/YYYY format in the date box to filter."


@app.callback(
    Output("product_launch_trend_category", "figure"),
    inputs=[
        Input("source", "value"),
        Input("category", "value"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_category_product_launch_figure(
    source: str, category: list, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    fig = create_category_product_launch_figure(
        meta_product_launch_trend_category_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
    return fig


@app.callback(
    Output("product_trend_category_name", "children"),
    [
        Input("product_launch_trend_category", "clickData"),
    ],
)
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
        return "Selected Category: bath-body"


@app.callback(
    Output("product_launch_trend_subcategory", "figure"),
    [
        Input("source", "value"),
        Input("product_launch_trend_category", "clickData"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_product_type_product_launch_figure(
    source: str, clickData, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    if clickData is not None:
        category = clickData["points"][0]["customdata"][0]
    else:
        category = "bath-body"

    fig = create_product_type_product_launch_figure(
        data=meta_product_launch_trend_product_type_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
    return fig


@app.callback(
    Output("product_launch_intensity_category", "figure"),
    inputs=[
        Input("source", "value"),
        Input("category", "value"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_product_launch_intensity_figure(
    source: str, category: list, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    fig = create_product_launch_intensity_figure(
        product_launch_intensity_category_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
    return fig


@app.callback(
    Output("ingredient_launch_trend_category", "figure"),
    inputs=[
        Input("source", "value"),
        Input("category", "value"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_category_new_ingredient_trend_figure(
    source: str, category: list, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    fig = create_category_new_ingredient_trend_figure(
        new_ingredient_trend_category_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
    return fig


@app.callback(
    Output("ingredient_trend_category_name", "children"),
    [
        Input("ingredient_launch_trend_category", "clickData"),
    ],
)
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
        return "Selected Category: bath-body"


@app.callback(
    Output("ingredient_launch_trend_subcategory", "figure"),
    [
        Input("source", "value"),
        Input("ingredient_launch_trend_category", "clickData"),
        Input("review_month_range", "start_date"),
        Input("review_month_range", "end_date"),
    ],
)
def update_product_type_new_ingredient_trend_figure(
    source: str, clickData, start_date: str, end_date: str
) -> go.Figure:
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
        start_date = dt.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
        start_date_string = start_date.strftime("%Y-%m-%d")
    else:
        start_date_string = default_start_date

    if end_date is not None:
        end_date = dt.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
        end_date_string = end_date.strftime("%Y-%m-%d")
    else:
        end_date_string = default_end_date

    if clickData is not None:
        category = clickData["points"][0]["customdata"][0]
    else:
        category = "bath-body"

    fig = create_product_type_new_ingredient_trend_figure(
        data=new_ingredient_trend_product_type_df,
        source=source,
        category=category,
        start_date=start_date_string,
        end_date=end_date_string,
    )
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
    [Output(f"page-{i}-link", "active") for i in range(1, 6)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False, False
    return [pathname == f"/page-{i}" for i in range(1, 6)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
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
        return ingredient_page_layout()
    # elif pathname == "/page-6":
    #     return "check this out. wip. yipee ki kay"
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1(
                "404: Not found",
                className="text-danger",
                style={"fontFamily": "GildaDisplay"},
            ),
            # html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server()
    # app.run_server(debug=True,port=2000)
