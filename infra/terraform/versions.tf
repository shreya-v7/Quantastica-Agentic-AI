terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }

  # Configure a remote state backend before running in shared environments.
  # backend "gcs" {
  #   bucket = "quantastica-tfstate"
  #   prefix = "env"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
