from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .stats import get_inventory_stats, get_sales_stats, get_sales_trend
from sales.models import Sales
from .report_generator import generate_csv, generate_filename
from .utils import get_period_range_from_request
from inventory.models import StockMovement


class DashboardView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, format=None):

        start_date, end_date, _ = get_period_range_from_request(request)
        dashboard_metrics = {}
        dashboard_metrics = {
            "this_period": {
                "sales": get_sales_stats(start_date, enddate=end_date),
                "inventory": get_inventory_stats(start_date, enddate=end_date),
            }
        }

        return Response(dashboard_metrics)


class SalesTrend(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        sales_trend = get_sales_trend(start=start_date, end=end_date)
        return Response(sales_trend)


class SalesReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        start_date, _ = get_period_range_from_request(request)
        file_name = generate_filename("sales")
        return generate_csv(filename=file_name, model=Sales, startdate=start_date)


class StockMovementView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        file_name = generate_filename("stockmovement")
        return generate_csv(
            filename=file_name, model=StockMovement, startdate=start_date
        )
