"""utility classes and functions for trend engine web-app."""
import gc
import io
import os
from pathlib import Path

import boto3
import pandas as pd


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
