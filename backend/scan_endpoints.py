import os
import sys
import django
import requests
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from hemis_client.services.hemis_api import HemisClient

logger = logging.getLogger(__name__)

def scan():
    client = HemisClient()
    base = client.api_url.rstrip('/')
    headers = client.headers
    
    candidates = [
        "/v1/data/education-form-list",
        "/v1/data/education-form",
        "/v1/data/education-forms",
        "/v1/data/education_form-list",
        "/v1/data/education_form",
        "/rest/v1/data/education-form-list", # sometimes /rest prefix repetition?
        "/data/education-form-list",
        # Maybe it's a classifier?
        "/v1/data/classifier-list?classifier=education_form",
        "/v1/data/classifier-list?name=education_form",
    ]
    
    print(f"Scanning from base: {base}")
    
    for path in candidates:
        url = f"{base}{path}"
        try:
            print(f"Trying: {url} ...", end=" ")
            resp = requests.get(url, headers=headers, params={"limit": 1}, timeout=5)
            print(f"[{resp.status_code}]")
            if resp.status_code == 200:
                print("SUCCESS!")
                print(resp.json())
                return
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    scan()
