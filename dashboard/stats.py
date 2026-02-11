from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models import Sum, Count, Avg, F

periods = {
    "this_month": "month",
    "last_three_months": "3_months",
    "this_year": "year",
    "today": "today",
}
from sales.models import Sales, Customer, SalesItem
from inventory.models import Product, StockMovement


def get_start_date(period: str):
    now = timezone.now()
    if period == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "3_months":
        month = (now.month - 3) % 12 or 12
        year = now.year if now.month > 3 else now.year - 1
        return now.replace(
            year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    elif period == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    else:
        raise ValueError("Invalid period. Use 'month', '3months', or 'year'.")


def get_sales_stats(startdate):
    total_sales = Sales.objects.filter(
        payment_status="completed", created_at__gte=startdate
    ).aggregate(total=Sum("total_amount"))

    highest_revenue_payment_method = (
        Sales.objects.values("payment_method")
        .filter(created_at__gte=startdate)
        .annotate(total_sales=Sum("total_amount"))
        .order_by("-total_sales")
    )
    cash_sales_revenue = Sales.objects.filter(
        payment_method="cash", created_at__gte=startdate
    ).aggregate(total=Sum("total_amount"), count=Count("id"))
    total_profit = (
        SalesItem.objects.filter(created_at__gte=startdate)
        .annotate(
            total_cost=F("quantity") * F("product__cost_price"),
            total_selling=F("quantity") * F("product__selling_price"),
        )
        .aggregate(
            total_cost_price=Sum("total_cost"), total_selling_price=Sum("total_selling")
        )
    )
    total_profit_amount = (total_profit["total_selling_price"] or 0) - (
        total_profit["total_cost_price"] or 0
    )
    top_selling_products = (
        SalesItem.objects.values("product__name")
        .filter(created_at__gte=startdate)
        .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("unit_price"))
        .order_by("-total_quantity")[:3]
    )
    top_customers = (
        Sales.objects.values("customer__name")
        .filter(created_at__gte=startdate)
        .annotate(total_orders=Count("id"), total_spent=Sum("total_amount"))
        .order_by("-total_spent")[:3]
    )
    top_categories = (
        SalesItem.objects.values("product__category__name")
        .filter(created_at__gte=startdate)
        .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("unit_price"))
        .order_by("-total_quantity")[:3]
    )

    return {
        "total_sales": total_sales["total"] or 0,
        "cash_sales_revenue": cash_sales_revenue,
        "total_profit_amount": total_profit_amount,
        "highest_revenue_payment_method": list(highest_revenue_payment_method),
        "top_selling_products": list(top_selling_products),
        "top_customers": list(top_customers),
        "top_categories": list(top_categories),
    }


def get_inventory_stats(start_date):
    total_refunds = (
        StockMovement.objects.filter(
            movement_type="IN",
            reason__in=["RETURN", "DAMAGED"],
            created_at__gte=start_date,
        )
        .values("movement_type", "reason")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    low_supply_products = Product.objects.filter(
        stock_quantity__lt=F("low_stock_limit"), created_at__gte=start_date
    )[:3]

    total_customers = Customer.objects.filter(created_at__gte=start_date).aggregate(
        customer_count=Count("id")
    )

    return {
        "total_refunds": list(total_refunds),
        "low_supply_products": list(
            low_supply_products.values("name", "stock_quantity", "low_stock_limit")
        ),
        "total_customers": total_customers["customer_count"],
    }
