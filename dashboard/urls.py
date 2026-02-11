from django.urls import path
from .views import DashboardView, SalesReportView

urlpatterns = [
    path("", view=DashboardView.as_view(), name="dashboard"),
    path("salesreport/", SalesReportView.as_view(), name="salesreport"),  # add /
]
