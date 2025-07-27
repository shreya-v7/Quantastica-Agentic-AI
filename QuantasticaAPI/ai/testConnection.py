import os
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError, Forbidden, ServiceUnavailable
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_gcp_connection_with_env():
    """
    Checks if the code is authenticated to GCP using the project ID from .env
    and by attempting to list storage buckets.
    """
    # Get the project ID from environment variables
    project_id = os.getenv('GCP_PROJECT')

    if not project_id:
        print("\n❌ Error: GCP_PROJECT environment variable not set.")
        print("Please ensure you have GCP_PROJECT=your-project-id in your .env file or set it manually.")
        return False

    try:
        # Initialize the client with the project ID from the environment
        storage_client = storage.Client(project=project_id)
        print(f"Attempting to connect to project: {project_id}")

        # Try to list a few buckets. This requires 'storage.buckets.list' permission.
        buckets = list(storage_client.list_buckets(max_results=1))

        if buckets is not None:
            print("\n✅ Successfully connected to GCP and authenticated!")
            print(f"Using Project ID: {storage_client.project}")
            print(f"Found {len(buckets)} bucket(s) (first one shown if exists):")
            for bucket in buckets:
                print(f"- {bucket.name}")
            return True
        else:
            print("\n❌ Connected to GCP, but no buckets found (or permission issue).")
            return False

    except Forbidden as e:
        print(f"\n❌ Authentication successful, but PERMISSION DENIED for project '{project_id}'.")
        print(f"Error: {e}")
        print("Ensure the authenticated account/service account has 'storage.buckets.list' permission.")
        return False
    except ServiceUnavailable as e:
        print(f"\n❌ Could not connect to GCP. Service unavailable or network issue.")
        print(f"Error: {e}")
        print("Check your network connection or the GCP service status.")
        return False
    except GoogleAPIError as e:
        print(f"\n❌ An API error occurred (likely authentication or configuration).")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
        if "google.auth.exceptions.DefaultCredentialsError" in str(e):
            print("Hint: It seems Application Default Credentials are not found.")
            print("  - If on local: Ensure GOOGLE_APPLICATION_CREDENTIALS is set and points to your service account key,")
            print("    or you ran `gcloud auth application-default login`.")
            print("  - If on GCP VM: Ensure a service account is attached to the VM with correct scopes.")
        return False
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        return False

# --- How to run the test ---
if __name__ == "__main__":
    check_gcp_connection_with_env()