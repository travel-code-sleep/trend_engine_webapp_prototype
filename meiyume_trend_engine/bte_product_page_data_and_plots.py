"""this module reads all the required data for product page of web-app, defines figure functions and create initial placeholder graphs."""
# import json
# import re
# import numpy as np
# from path import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from bte_utils import read_file_s3, set_default_start_and_end_dates

default_start_date, default_end_date = set_default_start_and_end_dates()

"""
Read all the data from flat files.
"""
# meta detail data
prod_page_metadetail_data_df = read_file_s3(
    filename="product_page_metadetail_data", file_type="feather"
)
prod_page_metadetail_data_df.product_name = (
    prod_page_metadetail_data_df.product_name.str.replace('"', "")
)
# pd.read_feather(
#     dash_data_path/'product_page_metadetail_data')
# review summary data
prod_page_review_sum_df = read_file_s3(
    filename="prod_page_product_review_summary", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'prod_page_product_review_summary')
# review talking points data
prod_page_review_talking_points_df = read_file_s3(
    filename="prod_page_review_talking_points", file_type="pickle"
)
# pd.read_pickle(
#     dash_data_path/'prod_page_review_talking_points')
# review sentiment and influence data
prod_page_review_sentiment_influence_df = read_file_s3(
    filename="prod_page_review_sentiment_influence", file_type="feather"
)

# pd.read_feather(
#     dash_data_path/'prod_page_review_sentiment_influence')
# review attribute data
prod_page_reviews_attribute_df = read_file_s3(
    filename="prod_page_reviews_attribute", file_type="feather"
)

# pd.read_feather(
#     dash_data_path/'prod_page_reviews_attribute')
# item data
prod_page_item_df = read_file_s3(filename="prod_page_item_data", file_type="feather")
# pd.read_feather(dash_data_path/'prod_page_item_data')
prod_page_item_price_df = prod_page_item_df[
    ["prod_id", "item_size", "meta_date", "item_price"]
]
prod_page_item_price_df["source"] = prod_page_item_price_df.prod_id.apply(
    lambda x: "us" if "sph" in x else "uk"
)
prod_page_item_price_df.reset_index(inplace=True, drop=True)

# ingredient data
prod_page_ing_df = read_file_s3(filename="prod_page_ing_data", file_type="feather")
# pd.read_feather(dash_data_path/'prod_page_ing_data')

""" create dropdown options """
product_page_source_options = [
    {"label": i, "value": i} for i in prod_page_metadetail_data_df.source.unique()
]
# product_page_category_options = [{'label': i, 'value': i}
#                                  for i in prod_page_metadetail_data_df.category.unique()]
# product_page_product_type_options = [{'label': i, 'value': i}
#                                      for i in prod_page_metadetail_data_df.product_type.unique()]
product_page_product_name_options = sorted(
    [
        {"label": i[0], "value": i[1]}
        for i in prod_page_metadetail_data_df[
            ["product_name", "prod_id"]
        ].values.tolist()
    ],
    key=lambda k: k["label"],
)

prod_page_user_attribute_options = sorted(
    [
        {"label": i, "value": i}
        for i in list(prod_page_reviews_attribute_df.columns.difference(["prod_id"]))
    ],
    key=lambda k: k["label"],
)

# category_page_user_attribute_options = [{'label': i, 'value': i}
#                                         for i in list(cat_page_reviews_by_user_attributes_df.columns.difference(
#                                             ['source', 'category', 'product_type']))]


""" create graph figure functions"""


def create_prod_page_review_talking_points_figure(
    data: pd.DataFrame, prod_id: str, col: str
) -> go.Figure:
    """create_prod_page_review_talking_points_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        prod_id (str): [description]
        col (str): [description]

    Returns:
        go.Figure: [description]
    """
    try:
        if len(data[col][data.prod_id == prod_id].values[0]) > 0:
            tpdf = pd.DataFrame(
                data[col][data.prod_id == prod_id].values[0], index=range(0, 1)
            ).T.reset_index()
            tpdf.columns = ["keyphrase", "frequency"]
            tpdf.sort_values(by="frequency", ascending=True, inplace=True)
        else:
            tpdf = None
    except Exception as ex:
        tpdf = None

    if tpdf is not None:
        if col == "pos_talking_points":
            title = "Positive Talking Points"
            marker_color = "green"
        else:
            title = "Negative Talking Points"
            marker_color = "red"

        fig = px.bar(
            tpdf,
            x="frequency",
            y="keyphrase",
            orientation="h",
            title=title,
            width=1000,
            height=600,
        )
        fig.update_traces(
            marker_color=marker_color,
            marker=dict(line=dict(color="rgb(8,48,107)", width=1.5)),
            opacity=0.5,
        )
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ""
        fig.update_layout(
            font_family="GothamLight",
            font_color="#c09891",
            title_font_family="GildaDisplay",
            title_font_color="#c09891",
            title_font_size=24,
            legend_title_font_color="green",
            hovermode="closest",
            xaxis={"title": "Frequency"},
            margin=go.layout.Margin(l=200),
        )
        fig.update_xaxes(
            tickfont=dict(family="GothamLight", color="crimson", size=12.5),
            title_font=dict(size=20, family="GothamLight", color="crimson"),
        )
        fig.update_yaxes(
            tickfont=dict(family="GothamLight", color="crimson", size=12.5),
            title_font=dict(size=20, family="GothamLight", color="crimson"),
        )
        return fig
    else:
        return {}


def create_prod_page_review_breakdown_figure(
    data: pd.DataFrame, prod_id: str, col: str
) -> go.Figure:
    """create_prod_page_review_breakdown_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        prod_id (str): [description]
        col (str): [description]

    Returns:
        go.Figure: [description]
    """
    df = pd.DataFrame(data[col][data.prod_id == prod_id].value_counts()).reset_index()
    df.columns = [col, "review_count"]
    df.sort_values(by=[col], inplace=True, ascending=False)

    if col == "sentiment":
        marker_colors = ["green", "red"]
    else:
        marker_colors = ["orange", "#c09891"]

    fig = px.pie(
        df,
        values="review_count",
        names=col,
        hole=0.4,
        height=400,
        width=450,
        title=f'Review {col.replace("_", " ").title()} Breakdown',
    )
    fig.update_layout(
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
    )
    fig.update_traces(marker_colors=marker_colors, pull=[0, 0.2])
    return fig


def create_prod_page_review_timeseries_figure(
    data: pd.DataFrame, prod_id: str, col: str
) -> go.Figure:
    """create_prod_page_review_timeseries_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        prod_id (str): [description]
        col (str): [description]

    Returns:
        go.Figure: [description]
    """
    if col == "is_influenced":
        data = data[data[col] == "yes"]
    if len(data[data.prod_id == prod_id]) > 0:
        df = pd.DataFrame(
            data[data.prod_id == prod_id]
            .groupby(by=["review_date"])[col]
            .value_counts()
        )
        df.columns = ["review_count"]
        df.reset_index(inplace=True)

        if col == "sentiment":
            marker_color = ["green", "red"]
            df.sort_values(by=[col, "review_date"], inplace=True, ascending=False)
        else:
            marker_color = ["#c09891", "orange"]

        fig = px.line(
            df,
            x="review_date",
            y="review_count",
            color=col,
            line_shape="spline",
            height=500,
            width=1000,
            color_discrete_sequence=marker_color,
            title=f"Reviews {col.title()} Over Time",
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
            yaxis={"title": "Review Count"},
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
    else:
        return {}


def create_prod_page_reviews_by_user_attribute_figure(
    prod_id: str, user_attribute: str = "age"
) -> go.Figure:
    """create_prod_page_reviews_by_user_attribute_figure [summary]

    [extended_summary]

    Args:
        prod_id (str): [description]
        user_attribute (str, optional): [description]. Defaults to 'age'.

    Returns:
        go.Figure: [description]
    """
    data = pd.DataFrame(
        prod_page_reviews_attribute_df[
            (prod_page_reviews_attribute_df.prod_id == prod_id)
        ][user_attribute].value_counts()
    ).reset_index()
    data.columns = [user_attribute, "review_count"]
    data = data[data[user_attribute] != ""]

    plot_title = user_attribute.replace("_", " ").title()
    fig = px.bar(
        data,
        x="review_count",
        y=user_attribute,
        orientation="h",
        height=400,
        # title=f"Reviews by {plot_title}",
        text="review_count",
    )
    fig.update_layout(
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Review Count"},
        yaxis={"categoryorder": "category descending", "title": user_attribute},
    )
    fig.update_xaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    fig.update_yaxes(
        tickfont=dict(family="GothamLight", color="crimson", size=14),
        title_font=dict(size=20, family="GothamLight", color="crimson"),
    )
    if user_attribute == "age":
        fig.update_layout(yaxis={"categoryorder": "category descending"})
    else:
        fig.update_layout(yaxis={"categoryorder": "total ascending"})

    return fig


def create_prod_page_reviews_distribution_figure(
    data: pd.DataFrame, prod_id: str
) -> go.Figure:
    """create_prod_page_reviews_distribution_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]
        prod_id (str): [description]

    Returns:
        go.Figure: [description]
    """
    rev_dist = pd.DataFrame(
        data[data.prod_id == prod_id].review_rating.value_counts()
    ).reset_index()
    rev_dist.columns = ["stars", "review_count"]
    fig = px.bar(
        rev_dist,
        x="review_count",
        y="stars",
        orientation="h",
        height=400,
        # title=f"Reviews by Stars",
        text="review_count",
    )
    fig.update_layout(
        font_family="GothamLight",
        font_color="#c09891",
        title_font_family="GildaDisplay",
        title_font_color="#c09891",
        title_font_size=24,
        legend_title_font_color="green",
        hovermode="closest",
        xaxis={"title": "Review Count"},
        yaxis={"categoryorder": "category descending", "title": "Stars"},
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


def create_prod_page_item_price_figure(data: pd.DataFrame) -> go.Figure:
    """create_prod_page_item_price_figure [summary]

    [extended_summary]

    Args:
        data (pd.DataFrame): [description]

    Returns:
        go.Figure: [description]
    """
    data = data.sort_values(by="meta_date")
    fig = px.line(
        data,
        x="meta_date",
        y="item_price",
        color="item_size",
        line_shape="spline",
        height=600,
        width=1000,
        #               color_discrete_sequence=marker_color,
        title=f"Price Over Time",
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
        yaxis={"title": "Price"},
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
# prod_page_pos_review_talking_points_figure =
