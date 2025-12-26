# backend/monitoring/urls.py
from django.urls import path
from .views import StudentContingentSummaryView, FacultyTableDataView, EmployeeListView, DepartmentListView
from .views_attendance import attendance_options_view, attendance_stat_view

urlpatterns = [
    path("student-contingent/", StudentContingentSummaryView.as_view()),
    path("faculty-table-data/", FacultyTableDataView.as_view()),

    # ✅ Attendance
    path("attendance/options/", attendance_options_view),
    path("attendance/stat/", attendance_stat_view),
    path("employee-list/", EmployeeListView.as_view()),
    path("department-list/", DepartmentListView.as_view()),

]
