from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SalesItemViewSet, SalesViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"salesitem", SalesItemViewSet, basename="salesitem")
router.register(r"sales", SalesViewSet, basename="sales")

urlpatterns = [path("", include(router.urls))]
