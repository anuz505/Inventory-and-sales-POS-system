from rest_framework import serializers
from inventory.models import Category, Product, StockMovement, Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "email", "phone", "address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "description",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "low_stock_limit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        if data.get("selling_price") and data.get("cost_price"):
            if data["selling_price"] < data["cost_price"]:
                raise serializers.ValidationError(
                    "Selling price cannot be less than cost price"
                )
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "movement_type",
            "reason",
            "user",
            "username",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
