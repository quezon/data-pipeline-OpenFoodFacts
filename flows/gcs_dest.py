import pandas as pd
import requests
import zipfile
import io
import os
import csv
from pathlib import Path
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket
from datetime import datetime
from dateutil.parser import parse

gcs_storage_block = GcsBucket.load(os.getenv("PREFECT_GCP_STR"))
parentFolder = "FoodData_Central_foundation_food_csv_2023-10-26"

@flow()
def copy():
  """Entry flow function to tasks and subflows"""
  logger = get_run_logger()
  url=f"https://fdc.nal.usda.gov/fdc-datasets/{parentFolder}.zip"
  pullZipFile(url)
  logger.info("INFO Successfully extracted CSV files to Local Folder")
  writeToStorageFromFolder()
  logger.info("INFO Successfully saved CSV to Cloud Storage")
  deleteFiles()
  logger.info(f"INFO Successfully deleted files in data/{parentFolder}")

@task()
def pullZipFile(data_zip_file: str):
  """Extract ZIP file downloaded from the web"""
  r = requests.get(data_zip_file)
  z = zipfile.ZipFile(io.BytesIO(r.content))
  z.extractall("data")

@flow()
def writeToStorageFromFolder() -> None:
  """Upload filenames included in 'files to read.txt' to GCS"""
  with open('files to read.txt') as filenames:
    for name in filenames:
      name2 = name.replace('\n','')
      path = f"data/{parentFolder}/{name2}.csv"
      df = pd.read_csv(path,quoting=csv.QUOTE_ALL,on_bad_lines='skip')
      cleaned_df = cleanDataFrame(df)
      rewriteFile(cleaned_df, path)
      gcs_storage_block.upload_from_path(path, path)

@task()
def rewriteFile(df: pd.DataFrame, path):
  """Rewrite to files after cleaning Dataframe"""
  path = Path(path).as_posix()
  df.to_csv(path)

@task()
def cleanDataFrame(df: pd.DataFrame):
  """
  Remove rows that don't comply with data format
  Assign a unform date format for a column
  """
  if 'min_year_acquired' in df.columns:
    df = df[df['min_year_acquired'].apply(lambda x: str(x).isdigit() or pd.isnull(x))]
  if 'publication_date' in df.columns:
    df['publication_date'] = df['publication_date'].apply(clean_date)
    df['publication_date'] = pd.to_datetime(df['publication_date']) 
  return df

@task()
def deleteFiles() -> None:
  """Delete CSV Files in the project folder"""
  folder = f"data/{parentFolder}"
  files = os.listdir(folder)
  for file in files:
    filePath = folder + '/'+ file
    os.remove(filePath)

def clean_date(text):
  """Make date format uniform"""
  datetimestr = parse(text)
  text = datetime.strptime(str(datetimestr)[:10], '%Y-%m-%d')
  return text

if __name__ == "__main__":
  copy()