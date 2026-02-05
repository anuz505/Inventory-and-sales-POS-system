from django.contrib import admin
from .models import Customer, Sales, SalesItem


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone_number", "address", "created_at"]
    search_fields = ["name", "email", "phone_number"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Customer Information",
            {"fields": ("name", "email", "phone_number", "address")},
        ),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


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
        "total_amount",
        "payment_method",
        "payment_status",
        "created_at",
    ]
    search_fields = ["invoice_number", "customer__name", "customer__email"]
    list_filter = ["payment_method", "payment_status", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [SalesItemInline]
    fieldsets = (
        ("Sale Information", {"fields": ("invoice_number", "customer", "user")}),
        (
            "Payment Details",
            {
                "fields": (
                    "subtotal",
                    "discount_amount",
                    "total_amount",
                    "payment_method",
                    "payment_status",
                )
            },
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


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
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        (
            "Item Information",
            {
                "fields": (
                    "sale",
                    "product",
                    "quantity",
                    "unit_price",
                    "discount_amount",
                    "subtotal",
                )
            },
        ),
        ("Metadata", {"fields": ("id", "created_at"), "classes": ("collapse",)}),
    )
