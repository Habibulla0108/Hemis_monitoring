import os
import sys
import django
import logging
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from hemis_client.services.hemis_api import HemisClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_missing():
    client = HemisClient()
    print("--- 1. Listing Faculties (Structure Type 11) ---")
    
    dept_data = client.get_department_list(limit=1000)
    items = dept_data.get('data', {}).get('items', [])
    
    faculties = []
    for item in items:
        stype = item.get('structureType', {})
        if str(stype.get('code')) == '11':
            faculties.append(item)
            
    print(f"Found {len(faculties)} faculties.")
    for f in faculties:
        print(f" - [{f['id']}] {f.get('name')}")
        
    # Pick a "missing" one from user screenshot context
    # User showed: Filologiya, Kompyuter, Magistratura, Telekommunikatsiya.
    # Missing likely: "Ijtimoiy-iqtisodiy fanlar fakulteti" or "Fizika-matematika fakulteti"
    
    target_name = "Fizika-matematika fakulteti"
    target_fac = next((f for f in faculties if f.get('name') == target_name), None)
    
    if not target_fac:
        target_name = "Ijtimoiy-iqtisodiy fanlar fakulteti"
        target_fac = next((f for f in faculties if f.get('name') == target_name), None)
        
    if target_fac:
        fid = target_fac['id']
        print(f"\n--- 2. Debugging Target: {target_fac.get('name')} (ID: {fid}) ---")
        
        # Test 1: Total Active
        t0 = time.time()
        count = client.get_student_count(department_id=fid, student_status_id=11)
        print(f"Total Active (Sync): {count} (Time: {time.time()-t0:.2f}s)")
        
        # Test 2: Breakdown by Education Form (Kunduzgi = 11)
        t0 = time.time()
        k_count = client.get_student_count(department_id=fid, education_form_id=11, student_status_id=11)
        print(f"Kunduzgi (11) Active (Sync): {k_count} (Time: {time.time()-t0:.2f}s)")
        
        # Test 3: Breakdown by Education Form (Sirtqi = 13)
        t0 = time.time()
        s_count = client.get_student_count(department_id=fid, education_form_id=13, student_status_id=11)
        print(f"Sirtqi (13) Active (Sync): {s_count} (Time: {time.time()-t0:.2f}s)")
    else:
        print(f"Could not find likely missing faculty '{target_name}' in list.")

if __name__ == "__main__":
    debug_missing()
