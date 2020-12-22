"""this module reads all the required data for product page of web-app, defines figure functions and create initial placeholder graphs."""
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
# ingredient data
# prod_page_ing_df = pd.read_feather(dash_data_path/'prod_page_ing_data')
ing_page_ing_df = read_file_s3(filename="ing_page_ing_data", file_type="feather")
ing_page_ing_df.category = ing_page_ing_df.category.astype(str)
ing_page_ing_df.product_type = ing_page_ing_df.product_type.astype(str)

# pd.read_feather(dash_data_path/'ing_page_ing_data')

""" create dropdown options """
ing_page_source_options = [
    {"label": i, "value": i} for i in ing_page_ing_df.source.unique()
]
ing_page_category_options = [
    {"label": i, "value": i} for i in ing_page_ing_df.category.unique()
]
ing_page_product_type_options = [
    {"label": i, "value": i} for i in ing_page_ing_df.product_type.unique()
]
ing_page_ingredient_options = [
    {"label": i, "value": i} for i in ing_page_ing_df.ingredient.unique()
]

""" create graph figure functions"""


def create_ing_page_ingredient_type_figure(
    source: str, category: str, product_type: str
) -> go.Figure:
    """create_ing_page_ingredient_type_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        go.Figure: [description]
    """
    data = pd.DataFrame(
        ing_page_ing_df[
            (ing_page_ing_df.source == source)
            & (ing_page_ing_df.category == category)
            & (ing_page_ing_df.product_type == product_type)
        ][["ingredient", "ingredient_type"]]
        .drop_duplicates(subset="ingredient")
        .ingredient_type.value_counts()
    ).reset_index()
    data.columns = ["ingredient_type", "count"]
    data.ingredient_type = data.ingredient_type.astype(str)
    data.ingredient_type[data.ingredient_type == ""] = "unclassified"

    fig = px.bar(
        data,
        x="count",
        y="ingredient_type",
        width=750,
        height=300,
        orientation="h",
        title="Ingredient Type Distribution",
        text="count",
    )
    fig.update_layout(
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        #         hovermode='closest',
        xaxis={
            "title": "Count",
            "categoryorder": "category descending",
        },
        yaxis={
            "title": "Ingredeint Type",
            "categoryorder": "total ascending",
        },
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


def create_ing_page_category_count_figure(
    data: pd.DataFrame, group: str, ingredient: str, orientation: str = "h"
) -> go.Figure:
    """create_ing_page_ingredient_type_figure [summary]

    [extended_summary]

    Args:
        source (str): [description]
        category (str): [description]
        product_type (str): [description]

    Returns:
        go.Figure: [description]
    """
    if orientation == "h":
        x = "product_count"
        y = group
        width = 750
        text = x
    else:
        x = group
        y = "product_count"
        if data.product_type.nunique() < 10:
            width = 1000
        else:
            width = 2000
        text = y

    fig = px.bar(
        data,
        x=x,
        y=y,
        width=width,
        height=500,
        orientation=orientation,
        title=f'Products Containing "{ingredient.title()}" by {group.replace("_", " ").title()}',
        hover_data=[group],
        hover_name=group,
        text=text,
    )

    fig.update_layout(
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": x.title()},
        yaxis={"title": y.title()},
    )

    if orientation == "h":
        fig.update_yaxes({"categoryorder": "total ascending"})
    else:
        fig.update_xaxes({"categoryorder": "total descending"})

    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    return fig
