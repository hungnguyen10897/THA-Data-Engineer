"""
Script to load init data to S3
"""
import os, time, boto3, asyncio
from pathlib import Path
import pandas as pd

bucket_name = "hung-tha-bucket"
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
      
      if quarter == '1.1' or quarter == '1.2':
         continue
   
      # if quarter == '1.1':
      #    quarter = 1

      # if quarter == '2' or quarter == '2.2':
      #    continue
   
      # if quarter == '2.1':
      #    quarter = 2


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
         file_name = file_path.stem
         s3_client = boto3.client('s3')
         print(f"\tUploading {file_path}")
         s3_client.upload_file(str(file_path), bucket_name, f"banner_images/{file_name}")


if __name__ == "__main__":
   upload_banner_images()
   upload_parquet_file()
