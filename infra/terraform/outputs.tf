output "server_url" {
  value       = google_cloud_run_v2_service.server.uri
  description = "Public URL of the API server."
}

output "postgres_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL connection name for the proxy."
}

output "redis_host" {
  value     = google_redis_instance.cache.host
  sensitive = true
}

output "exports_bucket" {
  value = google_storage_bucket.exports.name
}
