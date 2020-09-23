"""this module reads all the required data for category page of web-app, defines figure functions and create initial placeholder graphs."""
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from bte_utils import read_file_s3, set_default_start_and_end_dates

BANNED = "Banned?"
DATE_FIRST_REVIEWED = "Date (First Reviewed)"
INGREDIENT_TYPE = "ingredient_type"
NUMBER_OF_PRODUCTS = "Number of Products"
PACKAGING_SIZE = "Packaging Size"
PRICE_HIGH = "Price (High)"
PRICE_LOW = "Price (Low)"
PRODUCT_DESCRIPTION = "Product Description"
PRODUCT_RATING_ADJUSTED = "Product Rating (Adjusted)"

default_start_date, default_end_date = set_default_start_and_end_dates()

"""
Read all the data from flat files.
"""
# pricing data
cat_page_pricing_analytics_df = read_file_s3(
    filename="category_page_pricing_data", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'category_page_pricing_data')
# new products data
cat_page_new_products_count_df = read_file_s3(
    filename="category_page_new_products_count", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'category_page_new_products_count')
cat_page_new_products_details_df = read_file_s3(
    filename="category_page_new_products_details", file_type="feather"
)
renaming_cat_page_new_products_details_df_columns = {
    "product_name": PRODUCT_DESCRIPTION,
    "adjusted_rating": PRODUCT_RATING_ADJUSTED,
    "first_review_date": DATE_FIRST_REVIEWED,
    "small_size_price": PRICE_LOW,
    "big_size_price": PRICE_HIGH,
}
# cat_page_new_products_details_df.rename(
#     columns=renaming_cat_page_new_products_details_df_columns, inplace=True
# )
# pd.read_feather(
#     dash_data_path/'category_page_new_products_details')
# distinct brands/products data
cat_page_distinct_brands_products_df = read_file_s3(
    filename="category_page_distinct_brands_products", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'category_page_distinct_brands_products')
# # item variations and price data
cat_page_item_variations_price_df = read_file_s3(
    filename="category_page_item_variations_price", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'category_page_item_variations_price')
# item packaging data
cat_page_item_package_oz_df = read_file_s3(
    filename="category_page_item_package_oz", file_type="feather"
)
renaming_cat_page_item_package_oz_df_columns = {
    "item_size": PACKAGING_SIZE,
    "product_count": NUMBER_OF_PRODUCTS,
}
# cat_page_item_package_oz_df.rename(
#     columns=renaming_cat_page_item_package_oz_df_columns, inplace=True
# )
# pd.read_feather(
#     dash_data_path/'category_page_item_package_oz')
# top products data
cat_page_top_products_df = read_file_s3(
    filename="category_page_top_products", file_type="feather"
)
renaming_cat_page_top_products_df_columns = {
    "product_name": PRODUCT_DESCRIPTION,
    "adjusted_rating": PRODUCT_RATING_ADJUSTED,
    "first_review_date": DATE_FIRST_REVIEWED,
    "small_size_price": PRICE_LOW,
    "big_size_price": PRICE_HIGH,
}
# cat_page_top_products_df.rename(
#     columns=renaming_cat_page_top_products_df_columns, inplace=True
# )
# pd.read_feather(
#     dash_data_path/'category_page_top_products')
# new ingredients data
cat_page_new_ingredients_df = read_file_s3(
    filename="category_page_new_ingredients", file_type="feather"
)
renaming_cat_page_new_ingredients_df_columns = {
    "product_name": PRODUCT_DESCRIPTION,
    "ingredient_type": INGREDIENT_TYPE,
    "adjusted_rating": PRODUCT_RATING_ADJUSTED,
    "ban_flag": BANNED,
}
# cat_page_new_ingredients_df.rename(
#     columns=renaming_cat_page_new_ingredients_df_columns, inplace=True
# )
# pd.read_feather(
#     dash_data_path/'category_page_new_ingredients')
# review data
cat_page_reviews_by_user_attributes_df = read_file_s3(
    filename="category_page_reviews_by_user_attributes", file_type="feather"
)
# pd.read_feather(
#     dash_data_path/'category_page_reviews_by_user_attributes')

""" create dropdown options """
category_page_category_options = [
    {"label": i, "value": i} for i in cat_page_pricing_analytics_df.category.unique()
]
category_page_source_options = [
    {"label": i, "value": i} for i in cat_page_pricing_analytics_df.source.unique()
]
category_page_product_type_options = [
    {"label": i, "value": i}
    for i in cat_page_pricing_analytics_df.product_type.unique()
]
category_page_user_attribute_options = [
    {"label": i, "value": i}
    for i in list(
        cat_page_reviews_by_user_attributes_df.columns.difference(
            ["source", "category", "product_type"]
        )
    )
]

""" create graph figure functions"""


def create_reviews_by_user_attribute_figure(
    source: str = "us",
    category: str = "skincare",
    product_type: str = "acne-products-acne-cream",
    user_attribute: str = "age",
) -> go.Figure:
    """create_reviews_by_user_attribute_figure [summary]

    [extended_summary]

    Args:
        source (str, optional): [description]. Defaults to 'us'.
        category (str, optional): [description]. Defaults to 'skincare'.
        product_type (str, optional): [description]. Defaults to 'acne-products-acne-cream'.
        user_attribute (str, optional): [description]. Defaults to 'age'.

    Returns:
        go.Figure: [description]
    """
    data = pd.DataFrame(
        cat_page_reviews_by_user_attributes_df[
            (cat_page_reviews_by_user_attributes_df.source == source)
            & (cat_page_reviews_by_user_attributes_df.category == category)
            & (cat_page_reviews_by_user_attributes_df.product_type == product_type)
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
        hover_data=[user_attribute, "review_count"],
        height=400,
        # title=f"Reviews by {plot_title}",
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

    return fig


""" create initial figures/graphs. """
cat_page_user_attribute_figure = create_reviews_by_user_attribute_figure()
