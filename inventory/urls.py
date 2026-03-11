from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    SupplierViewSet,
    StockMovementViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"supplier", SupplierViewSet, basename="supplier")
router.register(r"stockmovement", StockMovementViewSet, basename="stockmovement")

urlpatterns = [path("", include(router.urls))]
