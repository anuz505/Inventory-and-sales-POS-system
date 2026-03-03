from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    CategorySerializer,
    StockMovementSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from .models import Category, Supplier, Product, StockMovement
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from .filters import ProductFilter, SupplierFilter, StockMovementFilter
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from sales.serializers import SalesSerializer
from rest_framework.response import Response
from sales.models import Sales


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination

    @method_decorator(cache_page(60 * 60 * 2, key_prefix="category"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related("supplier", "category")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter

    ordering_fields = [
        "name",
        "sku",
        "selling_price",
        "cost_price",
        "stock_quantity",
        "created_at",
    ]
    ordering = ["-created_at"]

    @method_decorator(cache_page(60 * 60 * 3, key_prefix="products"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SupplierFilter

    @method_decorator(cache_page(60 * 60 * 3, key_prefix="suppliers"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().prefetch_related("product", "sales", "user")
    serializer_class = StockMovementSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StockMovementFilter
    permission_classes = [IsAuthenticated]
