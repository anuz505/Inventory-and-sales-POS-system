from .views import HealthCheckView
from django.urls import path

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
