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
    print("Fetching Education Forms...")
    forms = client.get_education_forms()
    print(f"Found {len(forms)} forms.")
    for f in forms:
        print(f" - ID: {f.get('id')}, Name: {f.get('name')}, Code: {f.get('code')}")

if __name__ == "__main__":
    verify()
