"""utility classes and functions for trend engine web-app."""
import gc
import io
import os
from datetime import datetime as dt
from pathlib import Path

import boto3
import pandas as pd
from dateutil.relativedelta import relativedelta


def read_feather_s3(self, filename: str, prefix: str, bucket: str = 'meiyume-datawarehouse-prod') -> pd.DataFrame:
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


def set_default_start_and_end_dates():
    """

    Returns:
        default start date and default end date

    """
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
