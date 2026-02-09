from .serializers import CustomerSerialzer, SalesItemSerializer, SalesSerializer
from .models import Customer, SalesItem, Sales
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .invoice_generator import generate_invoice_pdf


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerialzer


class SalesItemViewSet(viewsets.ModelViewSet):
    queryset = SalesItem.objects.all()
    serializer_class = SalesItemSerializer


class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

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
        try:
            sale = self.get_object()
            pdf_buffer = generate_invoice_pdf(sale.id)

            filename = f"invoice_{sale.invoice_number}.pdf"

            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
                content_type="application/pdf",
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Error generating invoice: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
