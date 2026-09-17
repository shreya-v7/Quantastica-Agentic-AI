# Ops alert policies (Phase M/N). Notification channels are passed in so the same module
# works across environments. Thresholds are starting points; tune from real traffic.

resource "google_monitoring_alert_policy" "error_spike" {
  display_name = "${local.prefix} 5xx error spike"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run 5xx rate"
    condition_threshold {
      filter = join(" AND ", [
        "resource.type=\"cloud_run_revision\"",
        "metric.type=\"run.googleapis.com/request_count\"",
        "metric.label.response_code_class=\"5xx\"",
      ])
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.alert_notification_channels
}

resource "google_monitoring_alert_policy" "readiness_failing" {
  display_name = "${local.prefix} readiness failing"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failing"
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\""
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      duration        = "180s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }

  notification_channels = var.alert_notification_channels
}

resource "google_monitoring_alert_policy" "db_saturation" {
  display_name = "${local.prefix} DB CPU saturation"
  combiner     = "OR"

  conditions {
    display_name = "Cloud SQL CPU > 85%"
    condition_threshold {
      filter          = "metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.85
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_notification_channels
}

# Worker lag, LLM spend anomaly, and automated-trading volume anomaly are emitted as
# log-based metrics from the application (llm.usage, automation.fired, worker tick) and
# wired to alert policies here once the log metrics exist in the project.
