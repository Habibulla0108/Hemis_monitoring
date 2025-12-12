import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from monitoring.views import FacultyTableDataView, StudentContingentSummaryView

def test_views():
    factory = APIRequestFactory()
    request = factory.get('/')
    
    print("--- Testing FacultyTableDataView ---")
    try:
        view = FacultyTableDataView()
        # Mock request access
        view.request = request
        view.format_kwarg = None
        
        response = view.get(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Data keys:", response.data.keys())
        else:
            print("Error Data:", response.data)
    except Exception as e:
        print(f"CRASH in FacultyTableDataView: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- Testing StudentContingentSummaryView ---")
    try:
        view = StudentContingentSummaryView()
        view.request = request
        view.format_kwarg = None
        
        response = view.get(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Data keys:", response.data.keys())
        else:
            print("Error Data:", response.data)
    except Exception as e:
        print(f"CRASH in StudentContingentSummaryView: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_views()
