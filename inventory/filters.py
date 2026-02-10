from django_filters import rest_framework as filters
from django.db.models import F
from .models import Product, Supplier, Category, StockMovement


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Category
        fields = []


# TODO bug
class ProductFilter(filters.FilterSet):

    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    sku = filters.CharFilter(field_name="sku", lookup_expr="icontains")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")

    category = filters.UUIDFilter(field_name="category")

    supplier = filters.UUIDFilter(field_name="supplier")

    min_selling_price = filters.NumberFilter(
        field_name="selling_price", lookup_expr="gte"
    )
    max_selling_price = filters.NumberFilter(
        field_name="selling_price", lookup_expr="lte"
    )
    min_cost_price = filters.NumberFilter(field_name="cost_price", lookup_expr="gte")
    max_cost_price = filters.NumberFilter(field_name="cost_price", lookup_expr="lte")

    min_stock = filters.NumberFilter(field_name="stock_quantity", lookup_expr="gte")
    max_stock = filters.NumberFilter(field_name="stock_quantity", lookup_expr="lte")
    low_stock = filters.BooleanFilter(method="filter_low_stock")

    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at", lookup_expr="lte")

    ordering = filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("selling_price", "price"),
            ("cost_price", "cost"),
            ("stock_quantity", "stock"),
            ("created_at", "date"),
        )
    )

    def filter_low_stock(self, query_set, name, value):
        if value:
            return query_set.filter(stock_quantity__lte=F("low_stock_limit"))
        return query_set

    def filter_out_of_stock(self, query_set, name, value):
        if value:
            return query_set.filter(stock_quantity=0)
        return query_set

    class Meta:
        model = Product
        fields = []


class SupplierFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    phone = filters.CharFilter(field_name="phone", lookup_expr="icontains")
    address = filters.CharFilter(field_name="address", lookup_expr="icontains")
    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Supplier
        fields = []


class StockMovementFilter(filters.FilterSet):
    # Product filters
    product = filters.UUIDFilter(field_name="product__id")
    product_name = filters.CharFilter(
        field_name="product__name", lookup_expr="icontains"
    )
    product_sku = filters.CharFilter(field_name="product__sku", lookup_expr="icontains")

    movement_type = filters.ChoiceFilter(choices=StockMovement.MOVEMENT_TYPE_CHOICES)
    reason = filters.ChoiceFilter(choices=StockMovement.REASON_CHOICES)

    # User filter
    user = filters.UUIDFilter(field_name="user")

    # Sales reference
    sales = filters.UUIDFilter(field_name="sales")

    # Quantity range
    min_quantity = filters.NumberFilter(field_name="quantity", lookup_expr="gte")
    max_quantity = filters.NumberFilter(field_name="quantity", lookup_expr="lte")

    # Date filters
    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at", lookup_expr="lte")

    # Ordering
    ordering = filters.OrderingFilter(
        fields=(
            ("created_at", "date"),
            ("quantity", "quantity"),
        )
    )

    class Meta:
        model = StockMovement
        fields = []
