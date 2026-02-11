from django.urls import path
from .views import DashboardView

urlpatterns = [path("", view=DashboardView.as_view(), name="dashboard")]
