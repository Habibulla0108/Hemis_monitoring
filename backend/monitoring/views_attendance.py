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
        group_id = request.query_params.get("group_id")
        if not group_id:
            return Response({"error": "group_id is required"}, status=400)

        semester = request.query_params.get("semester")
        group_by = request.query_params.get("group_by") or "group"
        page = int(request.query_params.get("page") or 1)
        limit = int(request.query_params.get("limit") or 200)

        data = get_attendance_stat(
            group_id=int(group_id),
            semester=int(semester) if semester else None,
            group_by=group_by,
            page=page,
            limit=limit,
        )
        return Response(data)
    except Exception as e:
        logger.error("attendance_stat_view error: %s", e, exc_info=True)
        return Response({"error": str(e)}, status=500)
