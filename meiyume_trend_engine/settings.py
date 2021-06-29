import os

# load environment variable from .env file
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = 
S3_PREFIX = 
S3_REGION = 
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
