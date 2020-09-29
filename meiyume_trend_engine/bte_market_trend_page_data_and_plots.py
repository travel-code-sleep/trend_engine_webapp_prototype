"""this module reads all the required data for market trend page of web-app, defines figure functions and create initial placeholder graphs."""
import json
import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from path import Path

from bte_utils import read_file_s3, set_default_start_and_end_dates

default_start_date, default_end_date = set_default_start_and_end_dates()

"""
Read all the data from flat files.
"""
# review trend data
review_trend_category_df = read_file_s3(
    filename="review_trend_category_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'review_trend_category_month')
review_trend_product_type_df = read_file_s3(
    filename="review_trend_product_type_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'review_trend_product_type_month')

influenced_review_trend_category_df = read_file_s3(
    filename="review_trend_by_marketing_category_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'review_trend_by_marketing_category_month')
influenced_review_trend_product_type_df = read_file_s3(
    filename="review_trend_by_marketing_product_type_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'review_trend_by_marketing_product_type_month')

# product launch trend data
meta_product_launch_trend_category_df = read_file_s3(
    filename="meta_product_launch_trend_category_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'meta_product_launch_trend_category_month')
meta_product_launch_trend_product_type_df = read_file_s3(
    filename="meta_product_launch_trend_product_type_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'meta_product_launch_trend_product_type_month')
product_launch_intensity_category_df = read_file_s3(
    filename="meta_product_launch_intensity_category_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'meta_product_launch_intensity_category_month')

# ingredient trend data
new_ingredient_trend_category_df = read_file_s3(
    filename="new_ingredient_trend_category_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'new_ingredient_trend_category_month')
new_ingredient_trend_product_type_df = read_file_s3(
    filename="new_ingredient_trend_product_type_month", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'new_ingredient_trend_product_type_month')

""" create dropdown options """
market_trend_page_category_options = [
    {"label": i, "value": i} for i in review_trend_category_df.category.unique()
]
market_trend_page_source_options = [
    {"label": i, "value": i} for i in review_trend_category_df.source.unique()
]

"""create graph figure functions"""


def create_category_review_trend_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: list = review_trend_category_df.category.unique().tolist(),
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_category_review_trend_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (list, optional): [description]. Defaults to review_trend_category_df.category.unique().tolist().
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.month = data.month.astype(str)
    data = data[(data.month >= start_date) & (data.month <= end_date)]

    fig = px.area(
        data[(data.source == source) & (data.category.isin(category))],
        x="month",
        y="review_text",
        facet_col="category",
        facet_col_wrap=3,
        color="category",
        height=500,
        hover_data=["category"],
        facet_row_spacing=0.1,
        facet_col_spacing=0.06,
    )

    for axis in fig.layout:
        if type(fig.layout[axis]) == go.layout.YAxis:
            fig.layout[axis].title.text = ""
        if type(fig.layout[axis]) == go.layout.XAxis:
            fig.layout[axis].title.text = ""

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        annotations=list(fig.layout.annotations)
        + [
            go.layout.Annotation(
                x=-0.06,
                y=0.5,
                font=dict(size=20, color="crimson"),
                showarrow=False,
                text="Review Count",
                textangle=-90,
                xref="paper",
                yref="paper",
            )
        ],
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_size=24,
        title_font_color="#c09891",
        legend_title_font_color="green",
        hovermode="closest",
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_layout(showlegend=False)
    return fig


def create_product_type_review_trend_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: str = "bath-body",
    height: int = 1000,
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_product_type_review_trend_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (str, optional): [description]. Defaults to 'bath-body'.
        height (int, optional): [description]. Defaults to 1000.
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.month = data.month.astype(str)
    data = data[(data.month >= start_date) & (data.month <= end_date)]
    fig = px.area(
        data[(data.category == category) & (data.source == source)],
        x="month",
        y="review_text",
        facet_col="product_type",
        color="product_type",
        facet_col_wrap=5,
        height=height,
        facet_row_spacing=0.04,
        facet_col_spacing=0.06,
    )

    for axis in fig.layout:
        if type(fig.layout[axis]) == go.layout.YAxis:
            fig.layout[axis].title.text = ""
        if type(fig.layout[axis]) == go.layout.XAxis:
            fig.layout[axis].title.text = ""

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        annotations=list(fig.layout.annotations)
        + [
            go.layout.Annotation(
                x=-0.06,
                y=0.5,
                font=dict(size=20, color="crimson"),
                showarrow=False,
                text="Review Count",
                textangle=-90,
                xref="paper",
                yref="paper",
            )
        ],
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_size=24,
        title_font_color="#c09891",
        legend_title_font_color="green",
        hovermode="closest",
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
        showticklabels=True,
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_layout(showlegend=False)

    return fig


def create_category_product_launch_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: list = meta_product_launch_trend_category_df.category.unique().tolist(),
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_category_product_launch_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (list, optional): [description]. Defaults to meta_product_launch_trend_category_df.category.unique().tolist().
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.meta_date = data.meta_date.astype(str)
    data = data[(data.meta_date >= start_date) & (data.meta_date <= end_date)]

    fig = px.line(
        data[(data.source == source) & (data.category.isin(category))],
        x="meta_date",
        y="new_product_count",
        color="category",
        hover_data=["category"],
        hover_name="category",
        line_shape="spline",
        width=1200,
        height=600,
    )

    fig.update_traces(connectgaps=True, mode="markers+lines")

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Month"},
        yaxis={"title": "New Product Count"},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    return fig


def create_product_type_product_launch_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: str = "bath-body",
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_product_type_product_launch_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (str, optional): [description]. Defaults to 'bath-body'.
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.meta_date = data.meta_date.astype(str)
    data = data[(data.meta_date >= start_date) & (data.meta_date <= end_date)]

    fig = px.line(
        data[(data.source == source) & (data.category == category)],
        x="meta_date",
        y="new_product_count",
        color="product_type",
        line_group="category",
        hover_name="category",
        hover_data=["category", "product_type", "new_product_count"],
        line_shape="spline",
        width=1200,
        height=600,
    )

    fig.update_traces(connectgaps=True, mode="markers+lines")
    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Month"},
        yaxis={"title": "New Product Count"},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )

    return fig


def create_product_launch_intensity_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: list = product_launch_intensity_category_df.category.unique().tolist(),
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_product_launch_intensity_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (list, optional): [description]. Defaults to product_launch_intensity_category_df.category.unique().tolist().
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.meta_date = data.meta_date.astype(str)
    data = data[(data.meta_date >= start_date) & (data.meta_date <= end_date)]

    fig = px.bar(
        data[(data.source == source) & (data.category.isin(category))],
        x="meta_date",
        y="launch_intensity",
        color="category",
        hover_name="category",
        hover_data=["category", "launch_intensity", "new", "old"],
        width=1200,
        height=800,
    )

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Month"},
        yaxis={"title": "New Products Percentage within Category", "scaleratio": 1},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )

    return fig


def create_category_new_ingredient_trend_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: list = new_ingredient_trend_category_df.category.unique().tolist(),
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_category_new_ingredient_trend_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (list, optional): [description]. Defaults to new_ingredient_trend_category_df.category.unique().tolist().
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.meta_date = data.meta_date.astype(str)
    data = data[(data.meta_date >= start_date) & (data.meta_date <= end_date)]

    fig = px.line(
        data[(data.source == source) & (data.category.isin(category))],
        x="meta_date",
        y="new_ingredient_count",
        color="category",
        hover_data=["category"],
        hover_name="category",
        line_shape="spline",
        width=1200,
        height=600,
    )

    fig.update_traces(connectgaps=True, mode="markers+lines")

    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Month"},
        yaxis={"title": "New Ingredient Count"},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    return fig


def create_product_type_new_ingredient_trend_figure(
    data: pd.DataFrame,
    source: str = "us",
    category: str = "bath-body",
    start_date: str = default_start_date,
    end_date: str = default_end_date,
) -> go.Figure:
    """create_product_type_new_ingredient_trend_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        source (str, optional): [description]. Defaults to 'us'.
        category (str, optional): [description]. Defaults to 'bath-body'.
        start_date (str, optional): [description]. Defaults to default_start_date.
        end_date (str, optional): [description]. Defaults to default_end_date.

    Returns:
        go.Figure: [description]
    """
    data.meta_date = data.meta_date.astype(str)
    data = data[(data.meta_date >= start_date) & (data.meta_date <= end_date)]

    fig = px.line(
        data[(data.source == source) & (data.category == category)],
        x="meta_date",
        y="new_ingredient_count",
        color="product_type",
        line_group="category",
        hover_name="category",
        hover_data=["category", "product_type", "new_ingredient_count"],
        line_shape="spline",
        width=1200,
        height=600,
    )

    fig.update_traces(connectgaps=True, mode="markers+lines")
    fig.update_layout(
        # keep the original annotations and add a list of new annotations:
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Month"},
        yaxis={"title": "New Ingredient Count"},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )

    return fig


""" create initial figures/graphs. """
category_trend_figure = create_category_review_trend_figure(
    review_trend_category_df)
subcategory_trend_figure = create_product_type_review_trend_figure(
    review_trend_product_type_df
)

influenced_category_trend_figure = create_category_review_trend_figure(
    influenced_review_trend_category_df
)
influenced_subcategory_trend_figure = create_product_type_review_trend_figure(
    influenced_review_trend_product_type_df
)

product_launch_trend_category_figure = create_category_product_launch_figure(
    meta_product_launch_trend_category_df
)

product_launch_trend_subcategory_figure = create_product_type_product_launch_figure(
    meta_product_launch_trend_product_type_df
)

product_launch_intensity_category_figure = create_product_launch_intensity_figure(
    product_launch_intensity_category_df
)

new_ingredient_trend_category_figure = create_category_new_ingredient_trend_figure(
    new_ingredient_trend_category_df
)

new_ingredient_trend_product_type_figure = (
    create_product_type_new_ingredient_trend_figure(
        new_ingredient_trend_product_type_df
    )
)
