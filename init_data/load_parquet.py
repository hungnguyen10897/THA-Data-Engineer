"""
Script to load init data to S3
"""
import os
from pathlib import Path
import pandas as pd
import time

bucket = "s3://hungthas3"
init_data_path = "./csv"


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
   print(f"\t\tPrefilter rows: {df.shape[0]}")

   df.drop_duplicates(inplace= True)
   df.dropna(inplace= True)

   print(f"\t\tFiltered rows: {df.shape[0]}")
   return df

if __name__ == "__main__":
   for path in os.walk(init_data_path, topdown=True):
      
      print(f"PATH: {path}")
      quarter = path[0].split("/")[-1]

      if quarter == "csv":
         continue
      
      if quarter == '1' or quarter == '1.2':
         continue
   
      if quarter == '1.1':
         quarter = 1

      parentPath = Path(path[0])
      print(f"\tQUARTER: {quarter}")
      for file in path[2]:
         
         file_path = parentPath.joinpath(file)
         file_name = file_path.stem
         # print(f"\t\tFILE: {file_path.resolve()}")

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

         epoch_now = int(time.time())
         parquet_url = f"{bucket}/{table}/quarter={quarter}/{file_name}.parquet.snappy"
         # print("\t\t", parquet_url)
         # ??? partition_cols
         df.to_parquet(parquet_url, engine= "pyarrow",compression="snappy", index=False)
         print("\n")

# Publish banner images

