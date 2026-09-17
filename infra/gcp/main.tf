terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-south1"
}

resource "google_pubsub_topic" "recompute" {
  name = "household-recompute"
}

resource "google_pubsub_topic" "recompute_dlq" {
  name = "household-recompute-dlq"
}

resource "google_sql_database_instance" "book" {
  name             = "quantastica-book"
  database_version = "POSTGRES_16"
  region           = var.region
  settings {
    tier = "db-custom-2-7680"
    ip_configuration {
      ipv4_enabled = false
    }
  }
}

resource "google_storage_bucket" "olap" {
  name     = "${var.project_id}-book-events"
  location = var.region
}

resource "google_secret_manager_secret" "llm" {
  secret_id = "quantastica-llm"
  replication {
    auto {}
  }
}

output "topic" {
  value = google_pubsub_topic.recompute.id
}
