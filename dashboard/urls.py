from django.urls import path

from .views import DashboardView, SalesReportView, SalesTrend, StockMovementView

urlpatterns = [
    path("", view=DashboardView.as_view(), name="dashboard"),
    path("sales-report/", SalesReportView.as_view(), name="salesreport"),  # add /
    path("sales-trend/", SalesTrend.as_view(), name="salesTrend"),
    path("stock-movement/", StockMovementView.as_view(), name="stockMovement"),
]
