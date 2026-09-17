# This is plan-only infrastructure for asia-south1.

# Apply against an empty project after Workload Identity Federation is bound:
#   terraform -chdir=infra/gcp init
#   terraform -chdir=infra/gcp plan
#
# No long-lived keys. Cloud Run, Pub/Sub, Cloud SQL, GCS, Secret Manager.
# Portable to AWS Mumbai later; see docs/adr/001-cloud.md.
