
import os
import sys
import requests
import django

sys.path.append('d:\\hemis_monitoring\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hemis_client.services.hemis_api import HemisClient

client = HemisClient()
endpoint = f"{client.api_url}/v1/data/student-list"

def test(params):
    print(f"\nParams: {params}")
    p = params.copy()
    p['limit'] = 1
    try:
        r = requests.get(endpoint, headers=client.headers, params=p, timeout=10)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:100]}")
            return
        
        data = r.json()
        total = data.get('pagination', {}).get('totalCount')
        print(f"Total: {total}")
        
        items = data.get('data', {}).get('items', [])
        if items:
            s_status = items[0].get('studentStatus', {})
            print(f"First item studentStatus: {s_status}")
            
    except Exception as e:
        print(f"Ex: {e}")

# Baseline
test({})

# Try different studentStatus filters
test({'studentStatus': 11}) # Direct ID
test({'studentStatus[id]': 11}) # Nested ID
test({'_student_status': 11}) # Legacy
test({'student_status': 11}) # Snake case

# Try education form
test({'educationForm': 11})
test({'educationForm[id]': 11})
test({'_education_form': 11})
