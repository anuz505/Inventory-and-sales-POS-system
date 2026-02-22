from django.utils import timezone
from django.db.models import Sum, Count, F

from django.db.models.functions import TruncMonth

periods = {
    "this_month": "month",
    "last_three_months": "3months",
    "this_year": "year",
    "today": "today",
}
from .utils import get_prev_period
from sales.models import Sales, Customer, SalesItem
from inventory.models import Product, StockMovement


def get_trend(stat: str, start, end, stats_fn):
    prev_start_date, prev_end_date = get_prev_period(start, end)

    this_stat = stats_fn(startdate=start, enddate=end)[stat]
    prev_stat = stats_fn(startdate=prev_start_date, enddate=prev_end_date)[stat]
    diff = this_stat - prev_stat
    if diff > 0:
        trend = "increasing"
    elif diff < 0:
        trend = "declining"
    else:
        trend = "no_change"
    percentage = (diff / prev_stat * 100) if prev_stat > 0 else 100
    return {
        f"this_period_{stat}": this_stat,
        f"prev_period_{stat}": prev_stat,
        "difference": diff,
        "percentage_change": round(percentage, 2),
        "trend": trend,
    }


def get_sales_trend(start, end):
    sales_trend = get_trend(
        stats_fn=get_sales_stats, start=start, end=end, stat="total_sales"
    )
    return {"sales_trend": sales_trend}


def get_profit_trend(start, end):
    profit_trend = get_trend(
        stats_fn=get_sales_stats, start=start, end=end, stat="total_profit_amount"
    )
    return {"profit_trend": profit_trend}


def get_customers_trend(start, end):
    customer_trend = get_trend(
        stats_fn=get_inventory_stats, start=start, end=end, stat="total_customers"
    )
    return {"customer_trend": customer_trend}


def get_revenue_profit_data_vis(startdate, enddate):
    # group by months
    chart_data = (
        SalesItem.objects.filter(created_at__range=[startdate, enddate])
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            revenue=Sum(F("quantity") * F("unit_price")),
            profit=Sum(
                (F("quantity") * F("product__selling_price"))
                - (F("quantity") * F("product__cost_price"))
            ),
        )
        .order_by("month")
    )
    # formatted_data for frontend

    formatted_data = []
    for item in chart_data:
        revenue = item["revenue"] or 0
        profit = item["profit"] or 0
        profit_margin = round((profit / revenue * 100), 2) if revenue > 0 else 0
        formatted_data.append(
            {
                "month": item["month"].strftime("%b"),
                "revenue": revenue,
                "profit": profit,
                "profit_margin": profit_margin,
            }
        )
    return formatted_data


def get_sales_stats(startdate, enddate):
    total_sales = Sales.objects.filter(
        payment_status="completed", created_at__range=[startdate, enddate]
    ).aggregate(total=Sum("total_amount"))

    highest_revenue_payment_method = (
        Sales.objects.values("payment_method")
        .filter(created_at__range=[startdate, enddate])
        .annotate(total_sales=Sum("total_amount"))
        .order_by("-total_sales")
    )
    cash_sales_revenue = Sales.objects.filter(
        payment_method="cash", created_at__range=[startdate, enddate]
    ).aggregate(total=Sum("total_amount"), count=Count("id"))
    total_profit = (
        SalesItem.objects.filter(created_at__range=[startdate, enddate])
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
        .filter(created_at__range=[startdate, enddate])
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("unit_price")),
        )
        .order_by("-total_revenue")[:5]
    )

    top_customers = (
        Sales.objects.values("customer__name")
        .filter(created_at__range=[startdate, enddate])
        .annotate(total_orders=Count("id"), total_spent=Sum("total_amount"))
        .order_by("-total_spent")[:3]
    )
    top_categories = (
        SalesItem.objects.values("product__category__name")
        .filter(created_at__range=[startdate, enddate])
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("unit_price")),
        )
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


def get_inventory_stats(startdate, enddate):
    total_refunds = (
        StockMovement.objects.filter(
            movement_type="IN",
            reason__in=["RETURN", "DAMAGED"],
            created_at__range=[startdate, enddate],
        )
        .values("movement_type", "reason")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    low_supply_products = Product.objects.filter(
        stock_quantity__lt=F("low_stock_limit"), created_at__range=[startdate, enddate]
    )[:3]

    total_customers = Customer.objects.filter(
        created_at__range=[startdate, enddate]
    ).aggregate(customer_count=Count("id"))

    return {
        "total_refunds": list(total_refunds),
        "low_supply_products": list(
            low_supply_products.values("name", "stock_quantity", "low_stock_limit")
        ),
        "total_customers": total_customers["customer_count"],
    }
