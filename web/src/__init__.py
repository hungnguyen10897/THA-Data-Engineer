from flask import Flask
import os, redshift_connector, boto3

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ["FLASK_SECRET_KEY"]
app.config['UPLOAD_FOLDER'] =  'static/files'

conn = redshift_connector.connect(
   host = os.environ["REDSHIFT_HOST"],
   port = int(os.environ["REDSHIFT_PORT"]),
   database = os.environ["REDSHIFT_DATABASE"],
   user = os.environ["REDSHIFT_USER"],
   password = os.environ["REDSHIFT_PASSWORD"]
)

conn.autocommit = True
cursor = conn.cursor()

s3 = boto3.resource('s3')
bucket_name = "hungthas3"
bucket_url = f"s3://{bucket_name}"
bucket = s3.Bucket(bucket_name)

banner_images_url = os.environ["BANNER_IMAGES_URL"]

from src import routes
