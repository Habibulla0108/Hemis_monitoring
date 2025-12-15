# backend/monitoring/urls.py
from django.urls import path
from .views import StudentContingentSummaryView, FacultyTableDataView
from .views_attendance import attendance_options_view, attendance_stat_view

urlpatterns = [
    path("student-contingent/", StudentContingentSummaryView.as_view()),
    path("faculty-table-data/", FacultyTableDataView.as_view()),

    # ✅ Attendance
    path("attendance/options/", attendance_options_view),
    path("attendance/stat/", attendance_stat_view),

]
