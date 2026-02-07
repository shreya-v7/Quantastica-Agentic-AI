"""
Quantastica API -- Connectivity check before starting the server.
All credentials come from the single .env file.
"""

from app.config import settings


def main():
    print("Quantastica API -- Connectivity Check")
    print("=" * 40)

    if not settings.gcp_project:
        print("[ERROR] GCP_PROJECT not set in .env")
        return
    if not settings.gcp_private_key:
        print("[ERROR] GCP_PRIVATE_KEY not set in .env")
        return

    try:
        import vertexai
        creds = settings.get_gcp_credentials()
        vertexai.init(
            project=settings.gcp_project,
            location=settings.gcp_region,
            credentials=creds,
        )
        print(f"[OK] Vertex AI initialized (project={settings.gcp_project}, region={settings.gcp_region})")
    except Exception as e:
        print(f"[ERROR] Vertex AI init failed: {e}")
        return

    try:
        from testConnection import check_gcp_connection
        if check_gcp_connection():
            print("[OK] GCP connection verified")
        else:
            print("[WARN] GCP connection check returned False")
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return

    print()
    print("All checks passed. Start the server with:")
    print("  uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
