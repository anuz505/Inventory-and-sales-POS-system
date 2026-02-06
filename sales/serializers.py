from rest_framework import serializers
from sales.models import Customer, Sales, SalesItem
from django.db import transaction
from decimal import Decimal
from inventory.models import Product, StockMovement
import uuid


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
    # overrding the create function
    def create(self, validated_data):
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        items_data = validated_data.pop("items")
        sale = Sales.objects.create(invoice_number=invoice_number, **validated_data)
        subtotal = Decimal("0.00")

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]

            # Lock product for update to prevent race conditions
            product = Product.objects.select_for_update().get(pk=product.pk)

            item_subtotal = quantity * unit_price
            subtotal += item_subtotal
            # stock check
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {quantity}"
                )
            # sales items create
            SalesItem.objects.create(sale=sale, subtotal=item_subtotal, **item_data)

            # deducting stock from the products table
            product.stock_quantity -= quantity
            product.save()

            # creating new Stock movement for audit
            StockMovement.objects.create(
                product=product,
                quantity=quantity,
                movement_type="OUT",
                reason="SALE",
                sales=sale,
                user=validated_data.get("user"),
                notes=f"sale {invoice_number}",
            )
        sale.subtotal = subtotal
        sale.total_amount = subtotal - sale.discount_amount
        # new sale successfully saved
        sale.save()
        return sale
