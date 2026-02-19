from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    CategorySerializer,
    StockMovementSerializer,
)
from rest_framework import viewsets
from .models import Category, Supplier, Product, StockMovement
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from .filters import ProductFilter, SupplierFilter, StockMovementFilter
import django_filters.rest_framework as filters
from rest_framework.decorators import action
from sales.serializers import SalesSerializer
from rest_framework.response import Response
from sales.models import Sales


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related("supplier", "category")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # TODO remove this , only used for dev
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProductFilter

    @action(detail=True, methods=["get"])
    def sale(self, request, pk=None):
        product = self.get_object()
        sales = Sales.objects.filter(items__product=product).distinct()
        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]  # TODO remove this , only used for dev
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SupplierFilter


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().prefetch_related("product", "sales", "user")
    serializer_class = StockMovementSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = StockMovementFilter
    permission_classes = [AllowAny]  # TODO remove this , only used for dev
