from rest_framework import serializers
from sales.models import Customer, Sales, SalesItem
from django.db import transaction
from decimal import Decimal


class CustomerSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItem
        fields = "__all__"
        read_only_fields = ["id", "sale", "subtotal", "created_at"]


class SalesSerializer(serializers.ModelSerializer):
    items = SalesItemSerializer(many=True)

    class Meta:
        model = Sales
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "user",
            "subtotal",
            "total_amount",
            "invoice_number",
        ]

    @transaction.atomic
    # You must override create().
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        sale = Sales.objects.create(**validated_data)
        subtotal = Decimal("0.00")

        for item_data in items_data:
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]

            item_subtotal = quantity * unit_price
            subtotal += item_subtotal
            SalesItem.objects.create(sale=sale, subtotal=item_subtotal, **item_data)

        sale.subtotal = subtotal
        sale.total_amount = subtotal - self.discount_amount
        sale.save()
        return sale
