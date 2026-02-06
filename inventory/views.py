from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    CategorySerializer,
    StockMovementSerializer,
)
from rest_framework import viewsets
from .models import Category, Supplier, Product, StockMovement


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
