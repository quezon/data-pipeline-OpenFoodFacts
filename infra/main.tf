terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.21.0"
    }
    prefect = {
      source = "prefecthq/prefect"
    }
  }
}

provider "prefect" {
  api_key    = var.PREFECT_API_KEY
  account_id = var.PREFECT_ACCOUNT_ID
}

provider "google" {
  credentials = file(var.GCP_CREDENTIALS_FILE)
  project     = var.GCP_PROJECT
  region      = var.GCP_REGION
}

/*
resource "google_compute_address" "static" {
  name = "ipv4-address"
}

resource "google_compute_instance" "openff_vm" {
  name = var.GCP_CC_NAME
  machine_type = var.GCP_CC_TYPE
  zone = var.GCP_ZONE
  boot_disk {
    initialize_params {
      image = var.GCP_CC_OS_IMAGE
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static.address
    }
  }
}

resource "google_artifact_registry_repository" "openff_ar" {
  location      = var.GCP_REGION
  repository_id = var.GCP_AR_NAME
  description   = "Docker Repository for Open Food Facts"
  format        = "DOCKER"
}
*/

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

resource "google_storage_bucket" "openff_dp_staging_bucket" {
  name          = var.GCP_DATAPROC_STAGING_BUCKET
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

/*
resource "google_dataproc_cluster" "openff_dataproc" {
  name     = var.GCP_DATAPROC_NAME
  region   = var.GCP_REGION
  graceful_decommission_timeout = "120s"
  labels = {
    foo = "bar"
  }

  cluster_config {
    staging_bucket = var.GCP_DATAPROC_STAGING_BUCKET

    master_config {
      num_instances = 1
      machine_type  = "e2-medium"
      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances    = 1
      machine_type     = "e2-medium"
      min_cpu_platform = "Intel Skylake"
      disk_config {
        boot_disk_size_gb = 30
        num_local_ssds    = 1
      }
    }

    preemptible_worker_config {
      num_instances = 0
    }

    # Override or set some custom properties
    software_config {
      image_version = "2.0.35-debian10"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }

    gce_cluster_config {
      tags = ["hadoop", "spark", "batch"]
      # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
      service_account = var.GCP_SERVICE_ACCOUNT
      service_account_scopes = [
        "cloud-platform"
      ]
    }

    # You can define multiple initialization_action blocks
    initialization_action {
      script      = "gs://dataproc-initialization-actions/stackdriver/stackdriver.sh"
      timeout_sec = 500
    }
  }
}
*/