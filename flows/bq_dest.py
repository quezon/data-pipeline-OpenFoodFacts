import os
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from google.api_core.exceptions import BadRequest
from prefect_gcp.bigquery import BigQueryWarehouse, bigquery_insert_stream, bigquery_load_cloud_storage, bigquery_query

bigquery_warehouse_block = BigQueryWarehouse.load("dp-off-gcpbq")
gcp_credentials_block = GcpCredentials.load("dp-off-gcpcred")
gcs_storage_block = GcsBucket.load("dp-off-gstore")
parentFolder = "FoodData_Central_foundation_food_csv_2023-10-26"
bucket_name = os.getenv('TF_VAR_GCP_STORAGE_NAME')
dataset_name = os.getenv('TF_VAR_GCP_BQ_DATASET')
project=os.getenv("TF_VAR_GCP_PROJECT")
location=os.getenv("TF_VAR_GCP_LOCATION")

@flow(log_prints=True)
def insertMain():
    """Starting point for Insert"""
    filenames = getFilenames()
    # bucket = getBucket()
    performAllFileInserts(filenames)

@flow()
def performAllFileInserts(filenames) -> None:
    """Download data from GCS"""
    for name in filenames:
        insertSpecific(name)
    return

@flow
def insertSpecific(filename: str):
    """Logic of Inserting Records for Each CSV File"""
    # path = getGCSPathOfFile(filename)
    # df = convertToDataFrame(path)
    # cleaned_df = cleanDataFrame(df)
    # insertDataframeToTable(cleaned_df, filename)
    storageToBigQuery(filename)

@flow()
def storageToBigQuery(filename: str) -> None:
    deleteQuery = f"DELETE FROM {dataset_name}.{filename} WHERE 1=1"
    gcp_credentials_block = GcpCredentials.load("dp-off-gcpcred")

    try:
        bigquery_query(deleteQuery, gcp_credentials_block)
    except BadRequest as e:
        print('BadRequest Exception')
    finally:
        bigquery_load_cloud_storage(
            dataset=dataset_name,
            table=filename,
            uri=f"gs://{bucket_name}/data/{parentFolder}/{filename}.csv",
            gcp_credentials=gcp_credentials_block,
            job_config={
                "allow_quoted_newlines": True
            }
        )

@task()
def getFilenames():
    filenames=[]
    with open('files to read.txt') as file:
        for name in file:
            filenames.append(name.replace('\n',''))
    return filenames

@task()
def getBucket():
    return GcsBucket.load("dp-off-gstore")

@task()
def getGCSPathOfFile(filename: str):
    gcs_path = f"data/{parentFolder}/{filename}.csv"
    dir = gcs_storage_block.get_directory(from_path=gcs_path)
    return Path(dir[0])

@task()
def convertToDataFrame(path: Path) -> pd.DataFrame:
    """Read CSV from GCS and convert to DataFrame"""
    df = pd.read_csv(path)
    return df

@task()
def cleanDataFrame(df: pd.DataFrame):
    if 'min_year_acquired' in df.columns:
        df = df[df['min_year_acquired'].apply(lambda x: str(x).isdigit() or pd.isnull(x))]
    return df

@flow()
def insertDataframeToTable(df: pd.DataFrame, filename: str) -> None:
    """Insert DataFrame to a BiqQuery Table"""
    # df.to_gbq(
    #     destination_table = f"{os.environ["TF_VAR_GCP_BQ_DATASET"]}.openff_table",
    #     location = os.getenv("TF_VAR_GCP_LOCATION"),
    #     project_id = os.getenv("TF_VAR_GCP_PROJECT"),
    #     credentials=gcp_credentials_block.get_credentials_from_service_account(),
    #     chunksize=500_000,
    #     if_exists="replace"
    # )
    bigquery_insert_stream(
        dataset=dataset_name,
        table=filename,
        records=df.to_dict('records'), 
        gcp_credentials=gcp_credentials_block,
        project=project,
        location=location
    )

if __name__ == "__main__":
    insertMain()