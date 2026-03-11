from django.core.mail import EmailMessage
from celery import shared_task
from django.conf import settings

from users.models import User

from .invoice_generator import generate_invoice_pdf
from .models import Sales
from inventory.models import Product


@shared_task
def send_invoice_email_manually(sale_id: str):
    sale = Sales.objects.select_related("customer", "user").get(id=sale_id)
    customer_email = sale.customer.email
    subject = f"Invoice for Sale {sale.invoice_number}"
    message = f"""
Dear {sale.customer.name},

Thank you for your purchase!

Invoice Details:
Invoice Number: {sale.invoice_number}
Date: {sale.created_at.strftime("%Y-%m-%d")}
Total Amount: ${sale.total_amount}

Best regards,
{sale.user.username}
    """
    pdf_buffer = generate_invoice_pdf(sale.id)

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email],
    )
    email.attach(
        f"invoice_{sale.invoice_number}.pdf",
        pdf_buffer.getvalue(),
        "application/pdf",
    )
    email.send(fail_silently=False)


@shared_task
def send_low_stock_email(product_id: str):
    product = Product.objects.get(id=product_id)
    threshold = product.low_stock_limit

    print(
        f"Product: {product.name}",
        f"Stock: {product.stock_quantity}, Threshold: {threshold}",
    )

    if product.stock_quantity < threshold:
        subject = f"Low Stock Alert: {product.name}"
        message = f"""
            WARNING: Low Stock Alert

            Product ID: {product.id}
            Product Name: {product.name}
            Current Stock: {product.stock_quantity}
            Low Stock Limit: {threshold}

            Hope you will restock soon. 😊
        """

        admin_emails = User.objects.filter(is_staff=True).values_list(
            "email", flat=True
        )

        print(f"Admin emails: {list(admin_emails)}")

        if admin_emails:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=list(admin_emails),
                #   # Send to all admins
            )
            email.send(fail_silently=False)
