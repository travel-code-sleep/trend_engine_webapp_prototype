"""utility classes and functions for trend engine web-app."""
import base64
import gc
import io
import os
from datetime import datetime as dt
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError
from dateutil.relativedelta import relativedelta
from PIL import Image


def read_feather_s3(filename: str, prefix: str, bucket: str = 'meiyume-datawarehouse-prod') -> pd.DataFrame:
    """read_feather_s3 [summary]

    [extended_summary]

    Args:
        key (str): [description]

    Returns:
        pd.DataFrame: [description]
    """
    key = prefix+'/'+filename
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_feather(io.BytesIO(obj['Body'].read()))
    return df


def read_image_s3(prod_id: str, prefix: str = 'Feeds/BeautyTrendEngine/Image/Staging',
                  bucket: str = 'meiyume-datawarehouse-prod') -> str:
    """read_image_s3 [summary]

    [extended_summary]

    Args:
        prod_id (str): [description]
        prefix (str, optional): [description]. Defaults to 'Feeds/BeautyTrendEngine/Image/Staging'.
        bucket (str, optional): [description]. Defaults to 'meiyume-datawarehouse-prod'.

    Returns:
        str: [description]
    """
    try:
        key = prefix+'/' + f'{prod_id}/{prod_id}_image_1.jpg'
        # print(key)
        s3 = boto3.client('s3')
        product_image = s3.get_object(Bucket=bucket,
                                      Key=key)['Body'].read()
        product_image = Image.fromarray(
            np.array(Image.open(io.BytesIO(product_image))))
        product_image.save('images/temp_product_image.png')
        return 'images/temp_product_image.png'
    except ClientError as ex:
        return 'images/not_avlbl.jpg'


def set_default_start_and_end_dates():
    three_yrs_ago = dt.now() - relativedelta(years=3)
    default_start_date = str(pd.to_datetime(
        three_yrs_ago.strftime('%m/%d/%Y')))[:10].split('-')
    default_start_date[-1] = '01'
    default_start_date = ('-').join(default_start_date)

    default_end_date = str(pd.to_datetime(
        dt.today().strftime('%m/%d/%Y')))[:10].split('-')
    default_end_date[-1] = '01'
    default_end_date = ('-').join(default_end_date)
    return default_start_date, default_end_date
