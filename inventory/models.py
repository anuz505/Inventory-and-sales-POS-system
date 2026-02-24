from django.db import models
import uuid
from django.conf import settings


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.BigIntegerField()
    address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Suppliers"

    # def __str__(self):
    #     return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    low_stock_limit = models.IntegerField(default=10)
    created_at = models.DateTimeField(
        null=True, blank=True
    )  # TODO remove null and blank after populating db
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),  # for name searches
            models.Index(fields=["sku"]),  # for SKU lookups
            models.Index(fields=["category"]),  # for filtering by category
            models.Index(fields=["stock_quantity"]),  # for low stock queries
            models.Index(fields=["created_at"]),  # for recent products
        ]
        ordering = ["-created_at"]
        verbose_name_plural = "Products"

    # def __str__(self):
    #     return f"{self.name} (SKU: {self.sku})"


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]
    REASON_CHOICES = [
        ("SALE", "Sale"),
        ("PURCHASE", "Purchase"),
        ("RETURN", "Return"),
        ("MANUAL", "Manual Adjustment"),
        ("DAMAGED", "Damaged/Lost"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    reason = models.CharField(max_length=100, choices=REASON_CHOICES)
    sales = models.ForeignKey(
        "sales.Sales",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="stock_movement",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_movements",
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(
        blank=True, null=True
    )  # TODO remove after populating db

    class Meta:
        indexes = [
            models.Index(fields=["product", "created_at"]),
            models.Index(fields=["movement_type"]),
        ]
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"

    # def __str__(self):
    #     sale_ref = f" - Sale #{self.sales.id}" if self.sales else ""
    #     return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity}){sale_ref}"
