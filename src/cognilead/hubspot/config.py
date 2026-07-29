import os
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_SERVICE_KEY")

headers = {
    "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}