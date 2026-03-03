from django.core.mail import EmailMessage
from django.conf import settings
from users.models import User
from django.db.models.signals import post_save
from .models import Customer, Sales, SalesItem
from django.dispatch import receiver
from .invoice_generator import generate_invoice_pdf
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache


def send_invoice_email_manually(instance):
    """Reusable invoice sender — call from serializer when pending→completed."""
    customer_email = instance.customer.email
    subject = f"Invoice for Sale {instance.invoice_number}"
    message = f"""
Dear {instance.customer.name},

Thank you for your purchase!

Invoice Details:
Invoice Number: {instance.invoice_number}
Date: {instance.created_at.strftime("%Y-%m-%d")}
Total Amount: ${instance.total_amount}

Best regards,
{instance.user.username}
    """
    pdf_buffer = generate_invoice_pdf(instance.id)

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email],
    )
    email.attach(
        f"invoice_{instance.invoice_number}.pdf",
        pdf_buffer.getvalue(),
        "application/pdf",
    )
    email.send(fail_silently=False)


@receiver(post_save, sender=Sales)
def send_invoice_email(sender, instance, created, **kwargs):
    if created and instance.payment_status == "completed":
        send_invoice_email_manually(instance)
        return
    if getattr(instance, "_send_invoice_email", False):
        send_invoice_email_manually(instance)


@receiver(post_save, sender=SalesItem)
def send_low_stock_notification(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        threshold = product.low_stock_limit

        print(
            f"Product: {product.name}, Stock: {product.stock_quantity}, Threshold: {threshold}"
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
                print(f"Low stock email sent for {product.name}")


@receiver([post_save, post_delete], sender=Customer)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete_pattern("*customers*")
