variable "project_id" {
  type        = string
  description = "GCP project id."
}

variable "region" {
  type        = string
  default     = "asia-south1"
  description = "Deployment region (Mumbai by default for Indian users)."
}

variable "environment" {
  type        = string
  default     = "prod"
  description = "Environment name, used as a resource prefix."
}

variable "server_image" {
  type        = string
  description = "Fully qualified container image for the API server."
}

variable "worker_image" {
  type        = string
  description = "Container image for the background worker."
}

variable "db_tier" {
  type        = string
  default     = "db-custom-2-7680"
  description = "Cloud SQL machine tier."
}

variable "redis_memory_gb" {
  type        = number
  default     = 1
}

variable "alert_notification_channels" {
  type        = list(string)
  default     = []
  description = "Monitoring notification channel ids for ops alerts."
}
