from .serializers import CustomerSerialzer, SalesItemSerializer, SalesSerializer
from .models import Customer, SalesItem, Sales
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .invoice_generator import generate_invoice_pdf
from rest_framework.pagination import LimitOffsetPagination
import django_filters.rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .filters import CustomerFilters, SalesFilters, SalesItemFilters
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerialzer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CustomerFilters
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60 * 3, key_prefix="customers"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SalesItemViewSet(viewsets.ModelViewSet):
    queryset = SalesItem.objects.all()
    serializer_class = SalesItemSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SalesItemFilters
    permission_classes = [IsAuthenticated]


class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SalesFilters
    permission_classes = [IsAuthenticated]

    ordering_fields = ["created_at", "invoice_number"]

    def get_queryset(self):
        """
        Override to add distinct() when filtering by related items
        and prefetch related data for performance
        """
        queryset = (
            Sales.objects.all()
            .prefetch_related("items__product")
            .select_related("customer", "user")
        )
        # Apply distinct to avoid duplicates when filtering across relations
        if self.request.query_params:
            queryset = queryset.distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="download-invoice")
    def download_invoice(self, request, pk=None):
        """
        Download PDF invoice for a sale.
        GET /api-sales/sales/{id}/download-invoice/
        """
        sale = self.get_object()  # raises HTTP 404 automatically if not found
        try:
            pdf_buffer = generate_invoice_pdf(sale.id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Error generating invoice: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        filename = f"invoice_{sale.invoice_number}.pdf"
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
