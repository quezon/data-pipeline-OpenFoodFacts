import os
from prefect import flow, task
from prefect_gcp import GcpCredentials
from google.api_core.exceptions import BadRequest
from prefect_gcp.bigquery import bigquery_load_cloud_storage, bigquery_query

gcp_credentials_block = GcpCredentials.load(os.getenv("PREFECT_GCP_CRED"))

parentFolder = "FoodData_Central_foundation_food_csv_2023-10-26"

bucket_name = os.getenv('TF_VAR_GCP_STORAGE_NAME')
dataset_name = os.getenv('TF_VAR_GCP_BQ_DATASET')
project = os.getenv("TF_VAR_GCP_PROJECT")
location = os.getenv("TF_VAR_GCP_LOCATION")

@flow(log_prints=True)
def insertMain():
    """Entry flow function to tasks and subflows"""
    filenames = getFilenames()
    performAllFileInserts(filenames)

@flow()
def performAllFileInserts(filenames) -> None:
    """Move data from GCS to BigQuery"""
    for name in filenames:
        storageToBigQuery(name)
    return

@flow()
def storageToBigQuery(filename: str) -> None:
    """Perform Delete and Insert from csv file"""
    deleteQuery = f"DELETE FROM {dataset_name}.{filename} WHERE 1=1"
    tableExistsQuery = f"SELECT COUNT(1) FROM {dataset_name}.__TABLES__ WHERE table_id='{filename}'"

    result = bigquery_query(tableExistsQuery, gcp_credentials_block)

    if int(result[0][0]) == 1:
        bigquery_query(deleteQuery, gcp_credentials_block)

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
    """Delete CSV Filenames from 'files to read.txt'"""
    filenames=[]
    with open('files to read.txt') as file:
        for name in file:
            filenames.append(name.replace('\n',''))
    return filenames

if __name__ == "__main__":
    insertMain()