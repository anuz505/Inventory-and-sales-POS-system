from django.urls import path

from .views import (
    DashboardView,
    SalesReportView,
    StockMovementView,
    Trends,
    RevenueProfitVis,
)

urlpatterns = [
    path("", view=DashboardView.as_view(), name="dashboard"),
    path("sales-report/", SalesReportView.as_view(), name="salesreport"),  # add /
    path("trends/", Trends.as_view(), name="salesTrend"),
    path("stock-movement/", StockMovementView.as_view(), name="stockMovement"),
    path(
        "revenue-profit-chart/", RevenueProfitVis.as_view(), name="revenu-profit-chart"
    ),
]
