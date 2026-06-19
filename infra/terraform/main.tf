locals {
  prefix = "${var.environment}-quantastica"
}

# --- Networking -------------------------------------------------------------
resource "google_compute_network" "vpc" {
  name                    = "${local.prefix}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${local.prefix}-subnet"
  ip_cidr_range = "10.20.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_vpc_access_connector" "connector" {
  name          = "${local.prefix}-vpc-conn"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
}

# --- Postgres (Cloud SQL) ---------------------------------------------------
resource "google_sql_database_instance" "postgres" {
  name             = "${local.prefix}-pg"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL"
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "app" {
  name     = "quantastica"
  instance = google_sql_database_instance.postgres.name
}

# --- Redis (Memorystore) ----------------------------------------------------
resource "google_redis_instance" "cache" {
  name           = "${local.prefix}-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = var.redis_memory_gb
  region         = var.region
  redis_version  = "REDIS_7_0"

  authorized_network = google_compute_network.vpc.id
}

# --- Object storage (exports / documents) -----------------------------------
resource "google_storage_bucket" "exports" {
  name                        = "${local.prefix}-exports"
  location                    = var.region
  uniform_bucket_level_access = true
  versioning { enabled = true }
}

# --- Secrets ----------------------------------------------------------------
resource "google_secret_manager_secret" "app" {
  for_each  = toset(["jwt-secret", "database-url", "anthropic-api-key", "whatsapp-app-secret"])
  secret_id = "${local.prefix}-${each.key}"
  replication { auto {} }
}

# --- Run services -----------------------------------------------------------
resource "google_cloud_run_v2_service" "server" {
  name     = "${local.prefix}-server"
  location = var.region

  template {
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
    containers {
      image = var.server_image
      ports { container_port = 8000 }
      env {
        name  = "APP_ENV"
        value = "prod"
      }
      env {
        name  = "PLATFORM"
        value = "gcp"
      }
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
  }
}

resource "google_cloud_run_v2_service" "worker" {
  name     = "${local.prefix}-worker"
  location = var.region

  template {
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
    containers {
      image   = var.worker_image
      command = ["python", "-m", "app.workers"]
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 1
    }
  }
}
