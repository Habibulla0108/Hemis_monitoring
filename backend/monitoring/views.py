# backend/monitoring/views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .services import get_faculty_table_data, get_dashboard_summary
from hemis_client.services.hemis_api import HemisClient

logger = logging.getLogger(__name__)


class FacultyTableDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = get_faculty_table_data()
            return Response(data)
        except Exception as e:
            logger.error("FacultyTableDataView error: %s", e, exc_info=True)
            return Response({"error": str(e)}, status=500)


class StudentContingentSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = get_dashboard_summary()
            return Response(data)
        except Exception as e:
            logger.error("StudentContingentSummaryView error: %s", e, exc_info=True)
            return Response({"error": str(e)}, status=500)

class EmployeeListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            client = HemisClient()
            # Query paramlarni dict qilib yuboramiz
            params = request.query_params.dict()
            data = client.get_employee_list(params)
            return Response(data)
        except Exception as e:
            logger.error("EmployeeListView error: %s", e, exc_info=True)
            return Response({"error": str(e)}, status=500)

class DepartmentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            client = HemisClient()
            params = request.query_params.dict()
            # Default limit if not provided
            if "limit" not in params:
                 params["limit"] = 1000
            data = client.get_department_list(params=params)
            return Response(data)
        except Exception as e:
            logger.error("DepartmentListView error: %s", e, exc_info=True)
            return Response({"error": str(e)}, status=500)
