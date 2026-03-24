"""
GCP connectivity check -- uses centralized .env credentials.
No separate JSON key file needed.
"""

from app.config import settings


def check_gcp_connection():
    """
    Verifies GCP authentication by attempting to list storage buckets.
    All credentials come from the single .env file.
    """
    if not settings.gcp_project:
        print("[ERROR] GCP_PROJECT not set in .env")
        return False

    if not settings.gcp_private_key:
        print("[ERROR] GCP_PRIVATE_KEY not set in .env")
        return False

    try:
        from google.cloud import storage

        creds = settings.get_gcp_credentials()
        storage_client = storage.Client(
            project=settings.gcp_project, credentials=creds
        )
        print(f"Connecting to project: {settings.gcp_project}")
        buckets = list(storage_client.list_buckets(max_results=1))

        if buckets is not None:
            print(f"[OK] Connected to GCP project: {settings.gcp_project}")
            for bucket in buckets:
                print(f"  - Bucket: {bucket.name}")
            return True
        else:
            print("[WARN] Connected, but no buckets found.")
            return False

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    check_gcp_connection()
