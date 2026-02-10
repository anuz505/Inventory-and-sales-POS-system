from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    CategorySerializer,
    StockMovementSerializer,
)
from rest_framework import viewsets
from .models import Category, Supplier, Product, StockMovement
from rest_framework.decorators import action
from django.db.models import F
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from .filters import ProductFilter
import django_filters.rest_framework as filters


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # TODO remove this , only used for dev
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = ProductFilter
    # def get_queryset(self):
    #     query_set = super().get_queryset()
    #     params = self.request.query_params
    #     if params.get("low_stock") == "true":

    #         query_set = query_set.filter(stock_quantity__lt=F("low_stock_limit"))
    #     return query_set


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = LimitOffsetPagination


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    pagination_class = LimitOffsetPagination
