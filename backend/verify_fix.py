import os
import sys
import django
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from hemis_client.services.hemis_api import HemisClient
logging.basicConfig(level=logging.INFO)

def verify():
    client = HemisClient()
    
    # 1. Verify Total Active Students
    print("--- 1. Testing Total Active Students ---")
    total = client.get_student_count(student_status_id=11)
    print(f"Total Active Students: {total}")
    if total > 0:
        print("PASS: Total > 0")
    else:
        print("FAIL: Total is 0")

    # 2. Verify Specific Faculty (e.g., Structure ID 12 or 140 - try looking up one)
    print("\n--- 2. Testing Faculty Count ---")
    depts = client.get_department_list(limit=200)
    items = depts.get('data', {}).get('items', []) if isinstance(depts, dict) else []
    
    # Find active faculties
    faculties = [item for item in items if str(item.get('structureType', {}).get('code')) == '11']
    
    if not faculties:
        print("FAIL: No faculties found in API.")
        return

    test_faculty = faculties[0]
    fid = test_faculty['id']
    fname = test_faculty['name']
    
    print(f"Testing Faculty: {fname} (ID: {fid})")
    f_count = client.get_student_count(department_id=fid, student_status_id=11)
    print(f"Faculty Count: {f_count}")
    
    if f_count > 0:
        print("PASS: Faculty Count > 0")
    else:
        print("WARNING: Faculty Count is 0 (might be valid if really empty, but unlikely for top fac)")

    # 3. Verify Specific Education Form
    print("\n--- 3. Testing Education Form Count for Faculty ---")
    # Determine valid ed form
    ed_forms = client.get_education_forms()
    if not ed_forms:
        print("WARNING: No education forms found.")
        return
        
    for form in ed_forms[:3]: # Try first 3 forms
        form_id = form['id']
        form_name = form['name']
        print(f"Testing Form: {form_name} (ID: {form_id}) for Faculty {fid}")
        
        count = client.get_student_count(
            department_id=fid,
            education_form_id=form_id, 
            student_status_id=11
        )
        print(f"Count: {count}")
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    verify()
