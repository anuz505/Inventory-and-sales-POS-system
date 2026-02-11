from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .stats import periods, get_start_date, get_inventory_stats, get_sales_stats


class DashboardView(APIView):

    def get(self, request, format=None):
        dashboard_metrics = {}
        permission_classes = [AllowAny]

        for name, period in periods.items():
            start_date = get_start_date(period)
            dashboard_metrics[name] = {
                "sales": get_sales_stats(start_date),
                "inventory": get_inventory_stats(start_date),
            }

        return Response(dashboard_metrics)
