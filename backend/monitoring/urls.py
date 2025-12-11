from django.urls import path
from .views import StudentContingentSummaryView, FacultyTableDataView

urlpatterns = [
    path(
        "monitoring/student-contingent/",
        StudentContingentSummaryView.as_view(),
        name="student-contingent-summary",
    ),
    path(
        "monitoring/faculty-table/",
        FacultyTableDataView.as_view(),
        name="faculty-table-data",
    ),
]
