from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
import os

block_gcp_str = os.getenv("PREFECT_GCP_STR")
block_gcp_cred = os.getenv("PREFECT_GCP_CRED")
bucket_name = os.getenv("TF_VAR_GCP_STORAGE_NAME")

# Create GCP credentials block
credentials_block = GcpCredentials(
    service_account_info={} # enter your credentials from the json file
)
credentials_block.save(block_gcp_cred, overwrite=True)

# Create GCP storage block
bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load(block_gcp_cred),
    bucket=bucket_name,
)
bucket_block.save(block_gcp_str, overwrite=True)
