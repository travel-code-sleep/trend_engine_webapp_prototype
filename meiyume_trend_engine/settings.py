import os

# load environment variable from .env file
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = "meiyume-datawarehouse-prod"
S3_PREFIX = "Feeds/BeautyTrendEngine"
S3_REGION = "ap-southeast-1"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
