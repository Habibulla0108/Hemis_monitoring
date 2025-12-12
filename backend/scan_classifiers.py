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

def scan_classifiers():
    client = HemisClient()
    base = client.api_url.rstrip('/')
    headers = client.headers
    
    # Fetch ALL classifiers
    url = f"{base}/v1/data/classifier-list"
    print(f"Scanning ALL classifiers at {url}...")
    
    try:
        resp = requests.get(url, headers=headers, params={"limit": 200}, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("items", [])
        print(f"Total Classifiers: {len(items)}")
        for item in items:
            name = item.get('name', '')
            code = item.get('classifier', '')
            if 'ta\'lim' in name.lower() or 'education' in name.lower() or 'shakli' in name.lower() or 'form' in name.lower():
                print(f"MATCH: {name} (Code: {code})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_classifiers()
