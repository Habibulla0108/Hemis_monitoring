import os
import sys
import django
import requests
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings
from hemis_client.services.hemis_api import HemisClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def diagnose():
    client = HemisClient()
    base_url = client.api_url.rstrip('/')
    endpoint = "/v1/data/student-list"
    url = f"{base_url}{endpoint}"
    headers = client.headers

    print(f"--- Diagnosing HEMIS API: {url} ---")

    # 1. Baseline: No filters, limit=1
    print("\n1. Baseline Request (limit=1)")
    try_request(url, headers, {"limit": 1})

    # 2. Status Filters
    print("\n2. Testing Student Status Filters")
    # Test valid
    try_request(url, headers, {"_student_status": 11, "limit": 1})
    # Test invalid (should return 0 if filter works)
    print("Testing INVALID status (should be 0 if filter works):")
    try_request(url, headers, {"_student_status": 99999, "limit": 1})

    # ... (education form tests skipped for brevity in diff, keep them)

    # 4. Department/Faculty Filters
    print("\n4. Getting a valid Faculty ID (structureType=11)...")
    dept_id = get_valid_faculty_id(client)
    if dept_id:
        print(f"Using Faculty ID: {dept_id}")
        dept_params = [
            {"_department": dept_id},
        ]
        for p in dept_params:
            try_request(url, headers, {**p, "limit": 1})
            
        # 5. Combination Test
        print("\n5. Combination Test (Faculty + Ed Form)")
        try_request(url, headers, {
            "_department": dept_id,
            "_education_form": 11, # Kunduzgi
            "_student_status": 11,
            "limit": 1
        })
    else:
        print("Could not get a valid Faculty ID to test.")
        
    # 6. Check Education Forms Structure
    print("\n6. Checking Education Forms Structure")
    ef_url = f"{base_url}/v1/data/education-form-list"
    try:
        resp = requests.get(ef_url, headers=headers, params={"limit": 10}, timeout=10)
        print(f"Ed Form Status: {resp.status_code}")
        data = resp.json()
        print(f"Keys: {list(data.keys())}")
        if "data" in data:
            d = data["data"]
            if isinstance(d, dict):
                 print(f"data keys: {list(d.keys())}")
                 if "items" in d:
                     print(f"data.items type: {type(d['items'])}")
                     if len(d['items']) > 0:
                         print(f"First item: {d['items'][0]}")
            else:
                 print(f"data type: {type(d)}")
    except Exception as e:
        print(f"Ed Form Error: {e}")

def try_request(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Request: {params}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # Try to find total count
            pagination = data.get("pagination", {})
            total = pagination.get("totalCount") or pagination.get("total_count") or pagination.get("total")
            
            if total is None and isinstance(data.get("data"), dict):
                 pagination = data.get("data", {}).get("pagination", {})
                 total = pagination.get("totalCount")
            
            print(f"Total Count: {total}")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

def get_valid_faculty_id(client):
    try:
        # Try to get list of departments
        data = client.get_department_list(limit=200)
        items = data.get("data", {}).get("items", [])
        for item in items:
            stype = item.get("structureType", {})
            if str(stype.get("code")) == "11":
                print(f"Found Faculty: {item.get('name')} (ID: {item.get('id')})")
                return item.get("id")
    except:
        pass
    return None

if __name__ == "__main__":
    diagnose()
