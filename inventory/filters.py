from django_filters import rest_framework as filters
from django.db.models import F
from .models import Product


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    min_price = filters.NumberFilter(field_name="selling_price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="selling_price", lookup_expr="lte")
    category = filters.UUIDFilter(field_name="category", lookup_expr="iexact")
    sku = filters.CharFilter(field_name="sku", lookup_expr="iexact")

    low_stock = filters.BooleanFilter(method="filter_low_stock")
    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at", lookup_expr="lte")

    def filter_low_stock(self, query_set, name, value):
        if value:
            return query_set.filter(stock_quantity__lte=F("low_stock_limit"))
        return query_set

    class Meta:
        model = Product
        fields = []
