from django.contrib import admin
from .models import Category, Supplier, Product, StockMovement
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "address", "created_at", "updated_at"]
    search_fields = ["name", "email", "phone"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["name"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "quantity",
        "movement_type",
        "reason",
        "user",
        "sales",
        "notes",
        "created_at",
    ]
    search_fields = ["product", "movement_type", "reason", "user"]
    list_filter = ["user", "created_at", "reason", "movement_type", "sales"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "category",
        "supplier",
        "cost_price",
        "selling_price",
        "stock_quantity",
        "low_stock_alert",
    ]
    search_fields = ["name", "sku", "description"]
    list_filter = ["category", "supplier", "created_at", "stock_quantity"]
    readonly_fields = ["id", "created_at", "updated_at"]
    list_editable = ["cost_price", "selling_price", "stock_quantity"]
    ordering = ["-created_at"]

    def low_stock_alert(self, obj):
        if obj.stock_quantity <= obj.low_stock_limit:
            return format_html(
                '<span style="color: {}; font-weight: bold;">Low Stock</span>', "red"
            )
        return format_html(
            '<span style="color: {}; font-weight: bold;">OK</span>', "green"
        )

    low_stock_alert.short_description = "stock status"
