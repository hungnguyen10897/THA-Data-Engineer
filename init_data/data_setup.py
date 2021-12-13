"""
Script to load initial CSV files and banner images to S3.
Prepare Redshift Database, User, Tables and Stored Procedures
"""
import os, boto3, json, psycopg2
from pathlib import Path
import pandas as pd
from db.bootstrap_sql import bootstrap_queries

with open('data_setup_configs.json', 'r') as f:
   configs = json.load(f)

bucket_name = configs["BUCKET"]
bucket = f"s3://{bucket_name}"
init_data_path = "./csv"
image_path = "./images"


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
   df.drop_duplicates(inplace= True)
   df.dropna(inplace= True)
   return df


def upload_parquet_file():
   for path in os.walk(init_data_path, topdown=True):
      
      print(f"PATH: {path}")
      quarter = path[0].split("/")[-1]

      # Configure 
      if quarter == "csv":
         continue
      
      parentPath = Path(path[0])
      print(f"\tQUARTER: {quarter}")
      for file in path[2]:
         
         file_path = parentPath.joinpath(file)
         file_name = file_path.stem

         df = pd.read_csv(file_path)
         df = clean_df(df)

         # Get table name
         if "clicks" in file:
            table = "clicks"
         if "impressions" in file:
            table = "impressions"
         if "conversions" in file:
            table = "conversions"
         
         print(f"\t\t{table}")
         parquet_url = f"{bucket}/{table}/quarter={quarter}/{file_name}.parquet.snappy"
         # ??? partition_cols
         df.to_parquet(parquet_url, engine= "pyarrow",compression="snappy", index=False)


def upload_banner_images():
   for path in os.walk(image_path, topdown=True):
      parent = Path(path[0])
      for file in path[2]:
         file_path = parent.joinpath(file)
         file_name = file_path.name
         s3_client = boto3.client('s3')
         print(f"\tUploading {file_path}")
         s3_client.upload_file(str(file_path), bucket_name, f"banner_images/{file_name}")


def set_up_database():
   print("Bootstrapping Reshift Resources")
   REDSHIFT_HOST= configs["REDSHIFT_HOST"]
   REDSHIFT_PORT= configs["REDSHIFT_PORT"]
   REDSHIFT_DATABASE= configs["REDSHIFT_DATABASE"]
   REDSHIFT_MASTER_USER= configs["REDSHIFT_MASTER_USER"]
   REDSHIFT_MASTER_PASSWORD= configs["REDSHIFT_MASTER_PASSWORD"]

   conn = psycopg2.connect(
      user = REDSHIFT_MASTER_USER,
      password= REDSHIFT_MASTER_PASSWORD,
      host = REDSHIFT_HOST,
      port = int(REDSHIFT_PORT),
      database = REDSHIFT_DATABASE
   )
   conn.autocommit = True
   cursor = conn.cursor()

   for bootstrap_query in bootstrap_queries:
      sql = bootstrap_query.format(
            REDSHIFT_THA_USER= configs["REDSHIFT_THA_USER"],
            REDSHIFT_THA_USER_PASSWORD= configs["REDSHIFT_THA_USER_PASSWORD"],
            REDSHIFT_DATABASE = configs["REDSHIFT_DATABASE"],
            REDSHIFT_SPECTRUM_ROLE_ARN= configs["REDSHIFT_SPECTRUM_ROLE_ARN"],
            BUCKET = bucket_name
         )
      cursor.execute(sql)
      print(sql)

   conn.close()


if __name__ == "__main__":
   upload_banner_images()
   upload_parquet_file()
   set_up_database()
