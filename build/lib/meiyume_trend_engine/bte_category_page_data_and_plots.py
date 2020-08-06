"""this module reads all the required data for category page of web-app, defines figure functions and create initial placeholder graphs."""
import json
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from path import Path
from bte_utils import set_default_start_and_end_dates

dash_data_path = Path(r'D:\Amit\Meiyume\meiyume_bte_dash_flask_app\dash_data')

default_start_date, default_end_date = set_default_start_and_end_dates()

'''
Read all the data from flat files.
'''
# pricing data
cat_page_pricing_analytics_df = pd.read_feather(
    dash_data_path/'category_page_pricing_data')
# new products data
cat_page_new_products_df = pd.read_feather(
    dash_data_path/'category_page_new_products')
# distinct brands/products data
cat_page_distinct_brands_products_df = pd.read_feather(
    dash_data_path/'category_page_distinct_brands_products')
# item variations and price data
cat_page_item_variations_price_df = pd.read_feather(
    dash_data_path/'category_page_item_variations_price')
# item packaging data
cat_page_item_package_oz_df = pd.read_feather(
    dash_data_path/'category_page_item_package_oz')

''' create dropdown options '''
category_page_category_options = [{'label': i, 'value': i}
                                  for i in cat_page_pricing_analytics_df.category.unique()]
category_page_source_options = [{'label': i, 'value': i}
                                for i in cat_page_pricing_analytics_df.source.unique()]
category_page_product_type_options = [{'label': i, 'value': i}
                                      for i in cat_page_pricing_analytics_df.product_type.unique()]
