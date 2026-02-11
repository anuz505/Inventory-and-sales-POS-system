from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .stats import periods, get_start_date, get_inventory_stats, get_sales_stats
from django_filters import rest_framework as filters
from django.utils import timezone


class DashboardView(APIView):

    def get(self, request, format=None):
        period = request.query_params.get("period")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        dashboard_metrics = {}
        permission_classes = [AllowAny]

        if period:
            mapped_period = periods.get(period)
            if not mapped_period:
                mapped_period = "month"
            start_date = get_start_date(mapped_period)
        elif from_date:
            # if from_date is provided, parse it as date
            from datetime import datetime

            start_date = datetime.fromisoformat(from_date)
        else:
            start_date = get_start_date("month")  # default this month

            # start_date = get_start_date(period)
            # dashboard_metrics[period] = {
            #     "sales": get_sales_stats(start_date),
            #     "inventory": get_inventory_stats(start_date),
            # }

        # by default showing this month

        dashboard_metrics = {
            period
            or "this_period": {
                "sales": get_sales_stats(start_date),
                "inventory": get_inventory_stats(start_date),
            }
        }

        # for name, period in periods.items():
        #     start_date = get_start_date(period)
        #     dashboard_metrics[name] = {
        #         "sales": get_sales_stats(start_date),
        #         "inventory": get_inventory_stats(start_date),
        #     }

        return Response(dashboard_metrics)
