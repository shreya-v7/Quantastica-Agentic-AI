import requests

USER_ID = "u_123"
user_sessions = {}
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

url = f"{BASE_URL}/financial_news_analyzer/{USER_ID}"
print(url)
response = requests.post(url)

#prompt_url=f"{BASE_URL}/financial_analyzer/prompt/"

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.status_code, response.text)