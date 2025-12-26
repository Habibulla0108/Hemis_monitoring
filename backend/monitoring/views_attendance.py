import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .attendance_services import get_attendance_filter_options, get_attendance_stat

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def attendance_options_view(request):
    try:
        faculty_id = request.query_params.get("faculty_id")
        education_form_id = request.query_params.get("education_form_id")
        curriculum_id = request.query_params.get("curriculum_id")

        data = get_attendance_filter_options(
            faculty_id=int(faculty_id) if faculty_id else None,
            education_form_id=int(education_form_id) if education_form_id else None,
            curriculum_id=int(curriculum_id) if curriculum_id else None,
        )
        return Response(data)
    except Exception as e:
        logger.error("attendance_options_view error: %s", e, exc_info=True)
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def attendance_stat_view(request):
    try:
        faculty_id = request.query_params.get("faculty_id")
        if not faculty_id:
            return Response({"error": "faculty_id is required"}, status=400)

        education_type_id = request.query_params.get("education_type_id")
        education_form_id = request.query_params.get("education_form_id")
        semester_id = request.query_params.get("semester_id")

        page = int(request.query_params.get("page") or 1)
        limit = int(request.query_params.get("limit") or 200)

        data = get_attendance_stat(
            faculty_id=int(faculty_id),
            education_type_id=int(education_type_id) if education_type_id else None,
            education_form_id=int(education_form_id) if education_form_id else None,
            semester_id=int(semester_id) if semester_id else None,
            page=page,
            limit=limit,
        )
        return Response(data)
    except Exception as e:
        logger.error("attendance_stat_view error: %s", e, exc_info=True)
        return Response({"error": str(e)}, status=500)
