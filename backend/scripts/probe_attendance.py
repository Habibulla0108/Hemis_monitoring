import os
import sys
import django
import requests
import logging

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings

def probe():
    base = settings.HEMIS_BASE_URL
    token = settings.HEMIS_TOKEN
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints = [
        "/v1/data/group-list",
        "/v1/data/student-assignment-list", # sometimes used for linking students to groups
        "/v1/data/semester-list",
        "/v1/data/attendance-list", # Hypothetical
        "/v1/data/lesson-attendance-list", # Hypothetical
        "/v1/education/attendance-stats", # Hypothetical
    ]
    
    print(f"Probing HEMIS at {base}...")
    
    for ep in endpoints:
        url = f"{base}{ep}"
        try:
            print(f"Trying {ep}...", end=" ")
            resp = requests.get(url, headers=headers, params={'limit': 1}, timeout=5)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data:
                    print(f"  > Success! Keys: {data['data'].keys()}")
                    if 'items' in data['data'] and len(data['data']['items']) > 0:
                        print(f"  > Sample Item: {data['data']['items'][0].keys()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    probe()
