terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.21.0"
    }
  }
}

provider "google" {
  credentials = file(var.GCP_CREDENTIALS_FILE)
  project     = var.GCP_PROJECT
  region      = var.GCP_REGION
}

resource "google_storage_bucket" "openff_data_bucket" {
  name          = var.GCP_STORAGE_NAME
  location      = var.GCP_LOCATION
  force_destroy = true


  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}


resource "google_bigquery_dataset" "openff_dataset" {
  dataset_id = var.GCP_BQ_DATASET
  location   = var.GCP_LOCATION
}

