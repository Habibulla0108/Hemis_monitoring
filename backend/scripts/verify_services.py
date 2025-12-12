import os
import sys
import django
import logging

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from monitoring.services import get_faculty_table_data, get_dashboard_summary

def verify_service():
    print("--- 1. Testing get_faculty_table_data (Service) ---")
    data = get_faculty_table_data()
    
    # Check structure
    if 'columns' in data and 'rows' in data and 'totals' in data:
        print("PASS: Structure valid")
    else:
        print(f"FAIL: Invalid structure. Keys: {data.keys()}")
        return

    # Check content
    rows = data.get('rows', [])
    print(f"Rows count: {len(rows)}")
    if len(rows) > 0:
        print("PASS: Rows returned")
    else:
        print("WARNING: No rows (might be empty db)")

    total = data['totals']['grand_total']
    print(f"Grand Total: {total}")
    if total > 0:
        print("PASS: Grand Total > 0")
    else:
        print("FAIL: Grand Total is 0")

    print("\n--- 2. Testing get_dashboard_summary (Service) ---")
    summary = get_dashboard_summary()
    print(f"Summary Total: {summary.get('total_students')}")
    
    if summary.get('total_students') == total:
         print("PASS: Summary matches Table Total")
    else:
         print(f"FAIL: Mismatch! Summary: {summary.get('total_students')} vs Table: {total}")

if __name__ == "__main__":
    verify_service()
