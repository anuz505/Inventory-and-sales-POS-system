from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .stats import (
    get_customers_trend,
    get_inventory_stats,
    get_profit_trend,
    get_revenue_profit_data_vis,
    get_sales_stats,
    get_sales_trend,
)
from sales.models import Sales
from .report_generator import generate_csv, generate_filename
from .utils import get_period_range_from_request
from inventory.models import StockMovement
from internship_task.logger import LoggerSetup


class DashboardView(APIView):
    logger = LoggerSetup.setup_logger(__name__)
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        self.logger.info("Dashboard info")
        start_date, end_date, period = get_period_range_from_request(request)
        dashboard_metrics = {}
        dashboard_metrics = {
            period: {
                "sales": get_sales_stats(start_date, enddate=end_date),
                "inventory": get_inventory_stats(start_date, enddate=end_date),
            }
        }

        return Response(dashboard_metrics)


class Trends(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        sales_trend = get_sales_trend(start=start_date, end=end_date)
        profit_trend = get_profit_trend(start=start_date, end=end_date)
        customer_trend = get_customers_trend(start=start_date, end=end_date)
        return Response({**sales_trend, **profit_trend, **customer_trend})


class RevenueProfitVis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        chart_data = get_revenue_profit_data_vis(startdate=start_date,
                                                 enddate=end_date)
        return Response(chart_data)


class SalesReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        file_name = generate_filename("sales")
        return generate_csv(
            filename=file_name, model=Sales,
            startdate=start_date, enddate=end_date
        )


class StockMovementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        start_date, end_date, _ = get_period_range_from_request(request)
        file_name = generate_filename("stockmovement")
        return generate_csv(
            filename=file_name,
            model=StockMovement,
            startdate=start_date,
            enddate=end_date,
        )
