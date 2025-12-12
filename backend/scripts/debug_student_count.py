
import os
import sys
import requests
import django

sys.path.append('d:\\hemis_monitoring\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from hemis_client.services.hemis_api import HemisClient

client = HemisClient()

base_url = f"{settings.HEMIS_BASE_URL}/v1/data/student-list"
headers = client.headers

def check(label, params):
    print(f"\n--- Testing: {label} ---")
    print(f"Params: {params}")
    try:
        # Request with minimal limit to just get count
        p = params.copy()
        p['limit'] = 1
        p['page'] = 1
        r = requests.get(base_url, headers=headers, params=p, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            pagination = data.get("pagination", {})
            total = pagination.get("totalCount")
            print(f"Total Count: {total}")
            items = data.get("data", {}).get("items", [])
            if items:
                print(f"Sample Item Keys: {list(items[0].keys())}")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

# 1. No filters (Global count check)
check("No Filters", {})

# 2. Legacy underscore style (Current implementation)
check("Underscore Style (_student_status=11)", {"_student_status": 11})

# 3. CamelCase style
check("CamelCase Style (studentStatus=11)", {"studentStatus": 11})

# 4. Nested ID style
check("Nested ID Style (studentStatus[id]=11)", {"studentStatus[id]": 11})

# 5. Structure/Department Check
# Let's see if we can filter by faculty 
check("Underscore Department (_department=KEY)", {"_department": 149}) # ID 149 from previous debug output
check("CamelCase Department (department=KEY)", {"department": 149})
check("Structure Type (_structure_type=11)", {"_structure_type": 11})

