
import os
import django
import sys

# Setup Django
sys.path.append('d:\\hemis_monitoring\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hemis_client.services.hemis_api import HemisClient

try:
    print("Initializing HemisClient...")
    client = HemisClient()
    print("HemisClient initialized.")
    
    print("Testing get_education_forms...")
    forms = client.get_education_forms()
    print(f"Forms count: {len(forms)}")
    
    print("Testing get_department_list...")
    deps = client.get_department_list(limit=1)
    print("Department list fetched.")
    
    print("Testing get_student_count...")
    count = client.get_student_count(student_status_id=11)
    print(f"Total active students: {count}")
    
    print("SUCCESS: HemisClient is working.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
