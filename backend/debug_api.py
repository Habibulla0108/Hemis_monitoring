import os
import sys
import django
from django.conf import settings
from pathlib import Path
import requests
import urllib3

# Setup Django Environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

urllib3.disable_warnings()

def inspect():
    base = settings.HEMIS_BASE_URL
    token = settings.HEMIS_TOKEN
    headers = {'Authorization': f'Bearer {token}'}

    print(f"Testing with Base: {base}")

    # 1. Check Department List
    try:
        r = requests.get(f'{base}/v1/data/department-list?limit=10', headers=headers, verify=False)
        print("Dept List Status:", r.status_code)
        if r.status_code == 200:
            for item in r.json()['data']['items']:
                print(f"Dept: {item.get('name')} | Type: {item.get('structureType')} | Parent: {item.get('parent')}")
    except Exception as e:
        print("Dept Error:", e)

    # 2. Check Total Count in Student List (limit=1)
    try:
        # Test Filter by Code 11 (Kunduzgi)
        r = requests.get(f'{base}/v1/data/student-list?limit=1&_education_form=11', headers=headers, verify=False) 
        if r.status_code == 200:
            print("Count Code 11 (Kunduzgi):", r.json()['data']['pagination']['totalCount'])
        
        # Test Filter by Code 13 (Sirtqi)
        r = requests.get(f'{base}/v1/data/student-list?limit=1&_education_form=13', headers=headers, verify=False)
        if r.status_code == 200:
            print("Count Code 13 (Sirtqi):", r.json()['data']['pagination']['totalCount'])

    except Exception as e:
        print("Student Error:", e)

if __name__ == "__main__":
    inspect()
