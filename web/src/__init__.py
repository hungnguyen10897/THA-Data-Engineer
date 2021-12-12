from flask import Flask
import os, boto3, psycopg2, json
from psycopg2 import pool

app = Flask(__name__)

with open('flask_configs.json', 'r') as f:
   configs = json.load(f)

app.config['SECRET_KEY'] =  configs["FLASK_SECRET_KEY"]
app.config['UPLOAD_FOLDER'] =  'static/files'

connection_pool = psycopg2.pool.SimpleConnectionPool(
   1,
   200,
   user = configs["REDSHIFT_THA_USER"],
   password= configs["REDSHIFT_THA_USER_PASSWORD"],
   host = configs["REDSHIFT_HOST"],
   port = int(configs["REDSHIFT_PORT"]),
   database = configs["REDSHIFT_DATABASE"]
)

s3 = boto3.resource('s3')
bucket_name = configs["BUCKET"]
bucket_url = f"s3://{bucket_name}"
bucket = s3.Bucket(bucket_name)

banner_images_url = configs["BANNER_IMAGES_URL"]

from src import routes
