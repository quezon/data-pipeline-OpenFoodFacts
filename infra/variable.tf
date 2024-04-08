variable GCP_LOCATION {}
variable GCP_PROJECT {}
variable GCP_REGION {
    description = "Region of the GCP"
    type = string
    default = "us-east1"
}
variable GCP_ZONE {
    description = "Zone of the GCP"
    type = string
    default = "us-east1-c"
}
variable GCP_STORAGE_CLASS {
    description = "Storage Class of the GCP Bucket"
    type = string
    default = "STANDARD"
}
variable GCP_STORAGE_NAME {}
variable GCP_BQ_DATASET {}
variable GCP_CC_NAME {
    description = "Name of the GC Compute or Virtual Machine"
    type = string
    default = "OpenFoodFactsVM"
}
variable GCP_CC_TYPE {
    description = "Type of the GC Compute or Virtual Machine"
    type = string
    default = "n1-standard-1"
}
variable GCP_CC_OS_IMAGE {
    description = "Operating System Image of GC Compute or Virtual Machine"
    type = string
    default = "ubuntu-2310-mantic-amd64-v20240319"
}
variable GCP_DATAPROC_NAME {
    description = "Name of the GC Dataproc"
    type = string
    default = "openfoodfacts-dataproc"
}
variable GCP_DATAPROC_STAGING_BUCKET {
    description = "Name of the GC Datapro Staging bucket"
    type = string
    default = "openfoodfacts_stagingbucket"
}
variable GCP_CREDENTIALS_FILE {}
variable GCP_SERVICE_ACCOUNT {}

variable GCP_DATAFORM_REPO {
    description = "Name of the Dataform Repository"
    type = string
    default = "fooddatausda_dataf_repo"
}

variable GCP_DATAFORM_REPO_DNAME {
    description = "Display Name of the Dataform Repository"
    type = string
    default = "FoodData USDA Dataform Repository"
}

variable GIT_REPO {}
variable GIT_TOKEN {}

variable PREFECT_API_KEY {
    sensitive = true
}
variable PREFECT_ACCOUNT_ID {
    sensitive = true
}