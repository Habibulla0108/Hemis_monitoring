import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .services import get_faculty_table_data, get_dashboard_summary

logger = logging.getLogger(__name__)

class FacultyTableDataView(APIView):
    """
    Controller for the main Data Table.
    Delegates logic to the Service Layer.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = get_faculty_table_data()
            return Response(data)
        except Exception as e:
            logger.error(f"Faculty Table View Error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class StudentContingentSummaryView(APIView):
    """
    Controller for the Dashboard Summary Cards.
    Delegates logic to the Service Layer to ensure 100% data consistency with the Table.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = get_dashboard_summary()
            return Response(data)
        except Exception as e:
            logger.error(f"Summary View Error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=500)
