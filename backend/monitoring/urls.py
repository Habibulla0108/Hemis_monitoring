from django.urls import path
from .views import StudentContingentSummaryView, FacultyTableDataView

urlpatterns = [
    path("student-contingent/", StudentContingentSummaryView.as_view()),
    # path("student-contingent-matrix/", StudentContingentMatrixView.as_view()), # Removed as unused/refactored
    path("faculty-table-data/", FacultyTableDataView.as_view()), # New endpoint
]
