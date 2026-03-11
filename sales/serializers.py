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
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_price = serializers.DecimalField(
        source="product.selling_price",
        max_digits=10, decimal_places=2,
        read_only=True
    )
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SalesItem
        fields = "__all__"
        read_only_fields = ["sale", "subtotal", "created_at", "selling_price"]


class SalesSerializer(serializers.ModelSerializer):
    items = SalesItemSerializer(many=True)
    customer_name = serializers.CharField(
        source="customer.name", read_only=True)
    staff_name = serializers.CharField(source="user.username", read_only=True)

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
    def create(self, validated_data):
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        items_data = validated_data.pop("items")
        sale = Sales.objects.create(invoice_number=invoice_number,
                                    **validated_data)
        subtotal = Decimal("0.00")

        # Pass 1: lock products and validate stock
        locked_products = {}
        items_to_process = []

        for item_data in items_data:
            product = Product.objects.select_for_update().get(
                pk=item_data["product"].pk
            )
            quantity = item_data["quantity"]
            unit_price = product.selling_price
            item_subtotal = quantity * unit_price
            subtotal += item_subtotal

            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}, "
                    f"Requested: {quantity}"
                )

            locked_products[product.pk] = product
            items_to_process.append(
                (item_data, product, quantity, unit_price, item_subtotal)
            )

        # Pass 2: create items, deduct stock only if completed
        for (item_data, product, quantity, unit_price,
             item_subtotal) in items_to_process:
            SalesItem.objects.create(
                sale=sale, subtotal=item_subtotal,
                unit_price=unit_price, **item_data
            )

            if sale.payment_status == "completed":
                product.stock_quantity -= quantity
                product.save(update_fields=["stock_quantity"])
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
        sale.save()
        return sale

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Sales.objects.select_for_update().get(pk=instance.pk)
        old_status = instance.payment_status
        new_status = validated_data.get("payment_status", old_status)

        # --- Status transition guards ---
        if old_status == "refunded":
            raise serializers.ValidationError("Refunded cannot be modified")

        if old_status == "completed":
            client_keys = {k for k in validated_data.keys() if k != "user"}
            if new_status != "refunded" or len(client_keys) > 1:
                raise serializers.ValidationError(
                    "Completed sales can only be converted to refunded"
                )
            # --- Completed → Refunded ---
            instance.payment_status = new_status
            instance.save()
            self._refund_sale(instance)
            return instance

        # --- Pending: full edit allowed ---
        if old_status == "pending":
            instance.payment_status = new_status
            instance.notes = validated_data.get("notes", instance.notes)
            instance.customer = validated_data.get("customer",
                                                   instance.customer)
            instance.payment_method = validated_data.get(
                "payment_method", instance.payment_method
            )

            if "discount_amount" in validated_data:
                instance.discount_amount = validated_data["discount_amount"]

            if "items" in validated_data:
                self._update_items(instance, validated_data.pop("items"))

            self._recalculate_totals(instance)
            instance.save()

            if new_status == "completed":
                self._complete_sale(instance)
                instance._send_invoice_email = True
                instance.save()

            return instance

        return instance

    def _recalculate_totals(self, instance):
        discount = instance.discount_amount or Decimal("0.00")
        if discount > instance.subtotal:
            raise serializers.ValidationError(
                f"Discount ({discount}) cannot exceed ({instance.subtotal})"
            )
        instance.total_amount = instance.subtotal - discount

    def _update_items(self, instance, items_data):
        existing_items = {item.id: item for item in instance.items.all()}
        incoming_ids = {
            item_data.get("id") for item_data in items_data
            if item_data.get("id")
        }

        for item_id, item in existing_items.items():
            if item_id not in incoming_ids:
                item.delete()

        subtotal = Decimal("0.00")
        for item_data in items_data:
            product = Product.objects.select_for_update().get(
                pk=item_data["product"].pk
            )
            quantity = item_data["quantity"]
            unit_price = product.selling_price
            item_subtotal = quantity * unit_price
            subtotal += item_subtotal

            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}, "
                    f"Requested: {quantity}"
                )

            item_id = item_data.get("id")
            if item_id and item_id in existing_items:
                item = existing_items[item_id]
                item.quantity = quantity
                item.unit_price = unit_price
                item.subtotal = item_subtotal
                item.notes = item_data.get("notes", item.notes)
                item.save()
            else:
                item_data_clean = {k: v for k, v in item_data.items()
                                   if k != "id"}
                SalesItem.objects.create(
                    sale=instance,
                    subtotal=item_subtotal,
                    unit_price=unit_price,
                    **item_data_clean,
                )

        instance.subtotal = subtotal

    def _complete_sale(self, instance):
        sales_items = SalesItem.objects.filter(
            sale=instance
        ).select_related("product")

        # Pass 1: lock and validate all
        locked_products = {}
        for sale_item in sales_items:
            product = Product.objects.select_for_update().get(
                pk=sale_item.product.pk
                )
            locked_products[sale_item.id] = product
            if sale_item.quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}"
                    f"Requested: {sale_item.quantity}"
                )

        # Pass 2: mutate
        for sale_item in sales_items:
            product = locked_products[sale_item.id]
            product.stock_quantity -= sale_item.quantity
            product.save(update_fields=["stock_quantity"])

            StockMovement.objects.create(
                product=product,
                quantity=sale_item.quantity,
                movement_type="OUT",
                reason="SALE",
                sales=instance,
                user=instance.user,
                notes=f"sale {instance.invoice_number}",
            )

    def _refund_sale(self, instance):
        sales_items = SalesItem.objects.filter(
            sale=instance
        ).select_related("product")

        for sale_item in sales_items:
            product = Product.objects.select_for_update().get(
                pk=sale_item.product.pk
            )
            product.stock_quantity += sale_item.quantity
            product.save(update_fields=["stock_quantity"])

            StockMovement.objects.create(
                product=product,
                quantity=sale_item.quantity,
                movement_type="IN",
                reason="RETURN",
                sales=instance,
                user=instance.user,
                notes=f"Refund for sale {instance.invoice_number}",
            )
