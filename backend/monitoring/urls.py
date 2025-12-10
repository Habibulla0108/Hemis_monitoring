from django.urls import path
from .views import StudentContingentSummaryView

urlpatterns = [
    path(
        "monitoring/student-contingent/",
        StudentContingentSummaryView.as_view(),
        name="student-contingent-summary",
    ),
]
