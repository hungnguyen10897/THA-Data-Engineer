import redshift_connector, boto3, time
import pandas as pd
import numpy as np
from pathlib import Path

conn = redshift_connector.connect(
   host='hung-redshift-cluster.crdxyumc6dnp.eu-west-1.redshift.amazonaws.com',
   port=5439,
   database='tha',
   user='tha_admin',
   password='WJsXNo1TNw'
)

conn.autocommit = True
cursor = conn.cursor()

s3 = boto3.resource('s3')
bucket_name = "hungthas3"
bucket_url = f"s3://{bucket_name}"
my_bucket = s3.Bucket(bucket_name)

# Table Schemas
schemas = {
    "impressions": {
        "banner_id" : np.int64,
        "campaign_id" : np.int64
    },
    "clicks": {
        "click_id" : np.int64,
        "banner_id" : np.int64,
        "campaign_id" : np.int64
    },
    "conversions": {
        "conversion_id" : np.int64,
        "click_id" : np.int64,
        "revenue" : np.float64
    }
}


"""
Get banner ID for a campaign ID
"""
def get_banner_id(campaign_id: int, quarter: int) -> str:
    query = f"""
        SELECT * FROM
            (
                SELECT banner_id FROM revenues WHERE campaign_id = {campaign_id} AND quarter = {quarter} ORDER BY revenue DESC, number_of_clicks DESC LIMIT 10
            )
        ORDER BY RANDOM() LIMIT 1
    """

    cursor.execute(query)
    banner_id = cursor.fetchone()

    if banner_id is None:
        return None
    else:
        return banner_id[0]


"""
Preprocess DataFrame: Drop duplicate rows, Drop NA
"""
def preprocess_csv_file(df: pd.DataFrame, table: str) -> pd.DataFrame:
    print(f"\t\tPrefilter rows: {df.shape[0]}")

    # Preliminary Schema check
    expected_schema = pd.Series(schemas[table])
    if not expected_schema.equals(df.dtypes):
        return None

    df.drop_duplicates(inplace= True)
    df.dropna(inplace= True)

    print(f"\t\tFiltered rows: {df.shape[0]}")
    return df


"""
Deduplicate the DataFrame based on contents of remote table
"""
def deduplicate_content(df: pd.DataFrame, table: str, quarter: str):
    # Deduplication based on file content
    if table == "impressions":
        query_cols = ["banner_id", "campaign_id"]
    elif table == "clicks":
        query_cols = ["click_id"]
    elif table == "conversions":
        query_cols = ["conversion_id"]

    query = f"""
        SELECT {",".join(query_cols)} FROM ext_tha_schema.{table} WHERE quarter = {quarter} AND NOT(banner_id = 410 AND campaign_id = 27)
    """

    cursor.execute(query)
    remote_df = cursor.fetch_dataframe()

    # Assert there's alway data in the database
    assert(remote_df is not None)
    
    filter_na_col = "filter"
    remote_df[filter_na_col] = True
    joined_df = pd.merge(df, remote_df, how='left', on=query_cols)

    # Filter non-na 
    joined_df = joined_df[pd.isna(joined_df[filter_na_col])].drop(filter_na_col, axis=1)

    return joined_df


"""
Sequence of steps to synch new data with internal table 'tha.public.revenues'.
"""
def synch_with_internal_table(df: pd.DataFrame, table: str, quarter: int, file_name: str):

    # Upload to staging
    epoch_now = int(time.time())
    staging_table_name = f"{table}_{epoch_now}"
    staging_parquet_folder = f"{bucket_url}/staging/{staging_table_name}"
    staging_parquet_url = f"{staging_parquet_folder}/staging.parquet.snappy"
    print("\t\t", staging_parquet_url)

    df.to_parquet(staging_parquet_url, engine= "pyarrow",compression="snappy", index=False)

    # Create temporary external table
    cursor.execute(f"DROP TABLE IF EXISTS ext_tha_schema.{staging_table_name};")

    create_temp_table_query = f"""
        CREATE EXTERNAL TABLE ext_tha_schema.{staging_table_name}(
            banner_id INT8,
            campaign_id INT8
        )
        STORED AS PARQUET
        LOCATION '{staging_parquet_folder}';
    """
    cursor.execute(create_temp_table_query)

    # Triger synch with internal table by calling a stored_procedure
    synch_query = f"call public.synch_new_{table}('ext_tha_schema.{staging_table_name}', '{quarter}');"
    cursor.execute(synch_query)

    # Upload to permanent address
    permanent_parquet_url = f"{bucket_url}/{table}/quarter={quarter}/{file_name}.parquet.snappy"
    df.to_parquet(permanent_parquet_url, engine= "pyarrow",compression="snappy", index=False)

    # Remove staging table
    cursor.execute(f"DROP TABLE IF EXISTS ext_tha_schema.{staging_table_name};")

    # Remove staging file
    folder_prefix = staging_parquet_folder.split(bucket_url)[1]
    my_bucket.objects.filter(Prefix=staging_parquet_folder).delete()


"""
Clean and upload data
"""
def upload_csv(file_path: Path, table: str, quarter: int):

    df = pd.read_csv(file_path)
    df = preprocess_csv_file(df, table)

    if df is None:
        return (False, "Provided file doesn't conform to expected schema.")

    if df.empty:
        return (False, "All rows contain at least a NULL value")

    file_stem = file_path.stem
    
    # Deduplication based on filename
    folder = f"{table}/quarter={quarter}/"
    for object in my_bucket.objects.filter(Prefix=folder):
        object_name = object.key.split(folder)[1].split(".")[0]
        if file_stem == object_name:
            return (False, "A file with the same name already exists")

    df = deduplicate_content(df, table, quarter)
    if not df.empty:
        synch_with_internal_table(df, table, quarter)

