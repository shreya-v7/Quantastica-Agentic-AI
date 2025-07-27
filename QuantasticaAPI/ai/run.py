"""
Main runner script for QuantasticaAPI agents
Replaces the problematic 'adk run' command
"""
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def main():
    """Main function to run the agents"""
    print("🚀 Starting QuantasticaAPI Agents...")
    
    try:
        # Import and initialize Vertex AI
        import vertexai
        
        project_id = os.getenv('GCP_PROJECT')
        location = os.getenv('GCP_REGION', 'us-central1')
        
        if not project_id:
            print("❌ GCP_PROJECT environment variable not set")
            return
        
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI initialized for project: {project_id}")
        
        # Test connection
        print("🔍 Testing GCP connection...")
        from testConnection import check_gcp_connection_with_env
        if check_gcp_connection_with_env():
            print("✅ GCP connection successful!")
        else:
            print("❌ GCP connection failed")
            return
        
        # Run your agents here
        print("🤖 Agents are ready to use!")
        print("💡 Use the FastAPI server or import agents directly in your code")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return

if __name__ == "__main__":
    main()