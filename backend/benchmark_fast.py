import os
import sys
import django
from django.conf import settings
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Django Environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hemis_client.services.hemis_api import HemisClient

def benchmark():
    client = HemisClient()
    start = time.time()
    
    print("1. Fetching Departments...")
    dept_data = client.get_department_list(limit=1000)
    items = dept_data.get('data', {}).get('items', [])
    faculties = [i for i in items if i.get('structureType', {}).get('code') == '11']
    print(f"Found {len(faculties)} faculties.")

    ed_forms_map = {
        '11': "Kunduzgi", '12': "Kechki", '13': "Sirtqi", 
        '14': "Masofaviy", '15': "Ikkinchi mutaxassislik"
    }

    print("2. Parallel Counting...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for f in faculties:
            futures.append(executor.submit(client.get_student_count, _department=f['id'], _student_status=11))
        
        for code in ed_forms_map.keys():
            futures.append(executor.submit(client.get_student_count, _education_form=code, _student_status=11))
        
        results = [f.result() for f in as_completed(futures)]
        total = sum(results) # Loose sum just to check activity

    duration = time.time() - start
    print(f"Done! Duration: {duration:.2f} seconds.")

if __name__ == "__main__":
    benchmark()
