
import os
import django
import sys
import requests

# Setup Django
sys.path.append('d:\\hemis_monitoring\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hemis_client.services.hemis_api import HemisClient
from django.conf import settings

client = HemisClient()

def test_endpoint(name, method_name, **kwargs):
    print(f"\n--- Testing {name} ---")
    try:
        if method_name == "_get":
            res = client._get(kwargs['endpoint'], params=kwargs.get('params'))
            print(f"SUCCESS: {len(res.get('data', {}).get('items', []))} items found.")
        else:
            method = getattr(client, method_name)
            res = method(**kwargs)
            print(f"SUCCESS: Result: {res}")
    except Exception as e:
        print(f"FAILED: {e}")

print(f"Base URL: {settings.HEMIS_BASE_URL}")

# Test 1: Department List
test_endpoint("Department List", "get_department_list", limit=1)

# Test 2: Education Forms (The one that failed)
test_endpoint("Education Forms", "get_education_forms")

# Test 3: Student Count (The core feature)
test_endpoint("Student Count", "get_student_count", student_status_id=11)

# Test 4: Raw check for API root or version
try:
    print("\n--- Testing API Root ---")
    r = requests.get(f"{settings.HEMIS_BASE_URL}/v1/data/semester-list?limit=1", headers=client.headers)
    print(f"Semester List Status: {r.status_code}")
except Exception as e:
    print(f"Semester List Error: {e}")
