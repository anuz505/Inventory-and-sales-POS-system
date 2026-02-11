from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .stats import get_inventory_stats, get_sales_stats
from sales.models import Sales
from .report_generator import generate_csv, generate_filename
from .utils import get_startdate_from_request
from inventory.models import StockMovement


class DashboardView(APIView):

    def get(self, request, format=None):

        start_date, period = get_startdate_from_request(request)
        permission_classes = [AllowAny]
        dashboard_metrics = {}
        dashboard_metrics = {
            period
            or "this_period": {
                "sales": get_sales_stats(start_date),
                "inventory": get_inventory_stats(start_date),
            }
        }

        return Response(dashboard_metrics)


class SalesReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        start_date, _ = get_startdate_from_request(request)
        file_name = generate_filename("sales")
        return generate_csv(filename=file_name, model=Sales, startdate=start_date)


class StockMovementView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        start_date, _ = get_startdate_from_request(request)
        file_name = generate_filename("stockmovement")
        return generate_csv(
            filename=file_name, model=StockMovement, startdate=start_date
        )
