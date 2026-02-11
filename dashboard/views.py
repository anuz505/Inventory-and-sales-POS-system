from django.shortcuts import render
from sales.models import Sales, Customer, SalesItem
from inventory.models import Product, StockMovement

from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, F
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


# TODO more features
# Create your views here.
class DashboardView(APIView):
    def get(self, request, format=None):
        permission_classes = [AllowAny]

        # revenue
        total_sales = Sales.objects.filter(payment_status="completed").aggregate(
            total=Sum("total_amount"),
            count=Count("id"),
            average_order_value=Avg("total_amount"),
        )
        highest_revenue_payment_method = (
            Sales.objects.values("payment_method")
            .annotate(total_sales=Sum("total_amount"))
            .order_by("-total_sales")
        )
        cash_sales_revenue = Sales.objects.filter(payment_method="cash").aggregate(
            total=Sum("total_amount"), count=Count("id")
        )
        total_profit = SalesItem.objects.annotate(
            total_cost=F("quantity") * F("product__cost_price"),
            total_selling=F("quantity") * F("product__selling_price"),
        ).aggregate(
            total_cost_price=Sum("total_cost"), total_selling_price=Sum("total_selling")
        )
        total_profit_amount = (
            total_profit["total_selling_price"] - total_profit["total_cost_price"]
        )
        # top
        top_selling_products = (
            SalesItem.objects.values("product__name")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("unit_price"))
            .order_by("-total_quantity")[:3]
        )
        top_customers = (
            Sales.objects.values("customer__name")
            .annotate(total_orders=Count("id"), total_spent=Sum("total_amount"))
            .order_by("-total_spent")[:3]
        )
        top_categories = (
            SalesItem.objects.values("product__category__name")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("unit_price"))
            .order_by("-total_quantity")[:3]
        )

        # inventory
        total_refunds = (
            StockMovement.objects.filter(
                movement_type="IN", reason__in=["RETURN", "DAMAGED"]
            )
            .values("movement_type", "reason")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        low_supply_products = Product.objects.filter(
            stock_quantity__lt=F("low_stock_limit")
        )[:3]

        # totals

        total_customers = Customer.objects.aggregate(customer_count=Count("id"))

        return Response(
            {
                "sales": {
                    "total": total_sales["total"] or 0,
                    "count": total_sales["count"],
                    "cash_sales": {
                        cash_sales_revenue["total"],
                        cash_sales_revenue["count"],
                    },
                    "top_products": list(top_selling_products),
                    "top_customers": list(top_customers),
                    "top_categories": list(top_categories),
                    "total_profit": total_profit_amount,
                    "highest_revenue_payment_method": highest_revenue_payment_method,
                },
                "inventory": {
                    "customers": {"total_customers": total_customers["customer_count"]},
                    "low_supply_products": list(
                        low_supply_products.values(
                            "name", "stock_quantity", "low_stock_limit"
                        )
                    ),
                    "total_refunds": list(total_refunds),
                },
            }
        )
