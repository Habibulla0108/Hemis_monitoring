import os
import sys
import django
from django.conf import settings
from pathlib import Path
import requests
import urllib3

sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
urllib3.disable_warnings()
from hemis_client.services.hemis_api import HemisClient

def diagnose():
    client = HemisClient()
    
    print("--- DIAGNOSTICS ---")
    
    # 1. Global Total
    # Try fetching total WITHOUT any status filter first
    try:
        raw_total = client.get_student_count()
        print(f"Global Total (No filters): {raw_total}")
        
        active_total = client.get_student_count(_student_status=11)
        print(f"Active Total (Status 11): {active_total}")
    except Exception as e:
        print(f"Error fetching totals: {e}")
        return

    # 2. Education Form Sum
    forms_map = {
        '11': "Kunduzgi", '12': "Kechki", '13': "Sirtqi", 
        '14': "Masofaviy", '15': "Ikkinchi mutaxassislik"
    }
    form_sum = 0
    print("\n--- Education Forms ---")
    for code, name in forms_map.items():
        count = client.get_student_count(education_form_id=code, student_status_id=11)
        print(f"{name} ({code}): {count}")
        form_sum += count
    
    print(f"Sum of Forms: {form_sum} | Diff: {active_total - form_sum}")

    # 3. Faculty Sum
    print("\n--- Faculties ---")
    dept_data = client.get_department_list(limit=1000)
    items = dept_data.get('data', {}).get('items', [])
    faculties = [i for i in items if i.get('structureType', {}).get('code') == '11']
    
    fac_sum = 0
    for f in faculties:
        count = client.get_student_count(department_id=f['id'], student_status_id=11)
        print(f"{f['name']}: {count}")
        fac_sum += count
        
    print(f"Sum of Faculties: {fac_sum} | Diff: {active_total - fac_sum}")

if __name__ == "__main__":
    diagnose()
