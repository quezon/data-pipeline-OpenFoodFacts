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

resource "google_secret_manager_secret" "secret" {
  provider = google-beta
  secret_id = "git_secret"
  project = var.GCP_PROJECT

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_version" {
  provider = google-beta
  secret = google_secret_manager_secret.secret.id

  secret_data = var.GIT_TOKEN
}

resource "google_dataform_repository" "dataform_repository" {
  provider = google-beta
  name = var.GCP_DATAFORM_REPO
  display_name = var.GCP_DATAFORM_REPO_DNAME
  region   = var.GCP_REGION
  project = var.GCP_PROJECT
  npmrc_environment_variables_secret_version = google_secret_manager_secret_version.secret_version.id

  # labels = {
  #   label_foo1 = "label-bar1"
  # }

  git_remote_settings {
      url = var.GIT_REPO
      default_branch = "main"
      authentication_token_secret_version = google_secret_manager_secret_version.secret_version.id
  }

  workspace_compilation_overrides {
    default_database = var.GCP_PROJECT
    # schema_suffix = "_suffix"
    # table_prefix = "prefix_"
  }

  service_account = var.GCP_SERVICE_ACCOUNT
}