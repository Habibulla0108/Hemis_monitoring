import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hemis_client.services.hemis_api import HemisClient

def verify_counts():
    client = HemisClient()
    
    ed_forms_map = {
        '11': "Kunduzgi",
        '12': "Kechki",
        '13': "Sirtqi",
        '14': "Maxsus sirtqi",
        '15': "Ikkinchi oliy (sirtqi)",
        '16': "Masofaviy",
        '17': "Qo‘shma (sirtqi)",
        '18': "Ikkinchi oliy (kunduzgi)",
        '19': "Ikkinchi oliy (kechki)",
        '20': "Qo‘shma (kunduzgi)",
        '21': "Qo‘shma (kechki)",
        '22': "Ikkinchi oliy (masofaviy)",
        '23': "Qo‘shma (Masofaviy)"
    }
    
    print("-" * 50)
    print(f"{'ID':<5} | {'Name':<30} | {'Count':<10}")
    print("-" * 50)
    
    for code, name in ed_forms_map.items():
        try:
            # Check for active students (_student_status=11 is standard for 'active')
            count = client.get_student_count(education_form_id=code, student_status_id=11)
            print(f"{code:<5} | {name:<30} | {count:<10}")
        except Exception as e:
            print(f"{code:<5} | {name:<30} | ERROR: {e}")

if __name__ == "__main__":
    verify_counts()
