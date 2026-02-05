from django.contrib import admin
from .models import Customer, Sales, SalesItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone_number", "address", "created_at", "updated_at"]
    search_fields = ["name", "email", "phone_number"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]


class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1
    readonly_fields = ["id", "created_at"]
    fields = ["product", "quantity", "unit_price", "discount_amount", "subtotal"]


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "customer",
        "user",
        "subtotal",
        "discount_amount",
        "total_amount",
        "payment_method",
        "payment_status",
        "created_at",
    ]
    search_fields = ["invoice_number", "customer__name", "user__username"]
    list_filter = ["payment_method", "payment_status", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
    inlines = [SalesItemInline]


@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "product",
        "quantity",
        "unit_price",
        "discount_amount",
        "subtotal",
        "created_at",
    ]
    search_fields = ["sale__invoice_number", "product__name"]
    list_filter = ["created_at", "product"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]
