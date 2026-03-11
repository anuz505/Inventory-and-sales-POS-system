from django_filters import rest_framework as filters
from .models import Customer, Sales, SalesItem


class CustomerFilters(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    address = filters.CharFilter(field_name="address", lookup_expr="icontains")
    created_after = filters.DateFilter(field_name="created_at",
                                       lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at",
                                        lookup_expr="lte")

    class Meta:
        model = Customer
        fields = ["email", "phone_number"]


class SalesItemFilters(filters.FilterSet):
    product = filters.CharFilter(field_name="product", lookup_expr="exact")
    sale = filters.CharFilter(field_name="sale", lookup_expr="exact")

    class Meta:
        model = SalesItem
        fields = ["product", "sale"]


class SalesFilters(filters.FilterSet):
    invoice_number = filters.CharFilter(
        field_name="invoice_number", lookup_expr="exact"
    )
    created_after = filters.DateFilter(field_name="created_at",
                                       lookup_expr="gte")
    created_before = filters.DateFilter(field_name="created_at",
                                        lookup_expr="lte")
    min_discount = filters.NumberFilter(field_name="discount_amount",
                                        lookup_expr="gte")
    max_discount = filters.NumberFilter(field_name="discount_amount",
                                        lookup_expr="lte")
    min_total = filters.NumberFilter(field_name="total_amount",
                                     lookup_expr="gte")
    max_total = filters.NumberFilter(field_name="total_amount",
                                     lookup_expr="lte")

    # Filter by SalesItem properties
    product = filters.UUIDFilter(field_name="items__product_id",
                                 lookup_expr="exact")

    class Meta:
        model = Sales
        fields = [
            "product",
            "invoice_number",
            "user",
            "customer",
            "payment_method",
            "payment_status",
        ]
