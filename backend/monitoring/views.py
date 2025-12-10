# backend/monitoring/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny
from django.conf import settings
from django.core.cache import cache
from hemis_client.services.hemis_api import HemisClient, HemisAPIError


class StudentContingentSummaryView(APIView):
    permission_classes = [AllowAny]

    """
    HEMISdan talaba ro'yxatini olib, vaqtincha *faqat xom JSON* ni qaytaramiz.
    Shundan keyin grouping yozamiz.
    """

    def get(self, request):
        client = HemisClient()

        try:
            # TODO: Replace with actual HEMIS API endpoint and parameters
            # Example: "data/student-list" or "v1/students"
            endpoint = "REPLACE_WITH_ACTUAL_HEMIS_API_ENDPOINT"
            
            # Example params: {"university": settings.HEMIS_UNIVERSITY_CODE, "study_year": 2025}
            params = {} 

            cache_key = f"student_contingent_{endpoint}_{params}"
            payload = cache.get(cache_key)

            if not payload:
                payload = client._get(endpoint, params=params)
                cache.set(cache_key, payload, timeout=300) # 5 minutes

        except HemisAPIError as e:
            # Fallback to Mock Data if API fails (for demo/development purposes)
            logger.warning(f"HEMIS API failed ({e}), using MOCK DATA for demonstration.")
            return Response({
                "total_students": 12500,
                "faculty_counts": [
                    {"faculty_name": "Fizika-matematika", "count": 3200},
                    {"faculty_name": "Pedagogika", "count": 4100},
                    {"faculty_name": "San'atshunoslik", "count": 1500},
                    {"faculty_name": "Tabiiy fanlar", "count": 3700}
                ],
                "education_form_counts": [
                    {"form_name": "Kunduzgi", "count": 9800},
                    {"form_name": "Sirtqi", "count": 2700}
                ]
            })

        try:
            payload = resp.json()
        except ValueError:
             logger.error("HEMIS returned non-JSON response")
             raise HemisAPIError("Invalid JSON response from HEMIS")
