from django.core.mail import EmailMessage
from django.conf import settings
from users.models import User
from django.db.models.signals import post_save
from .models import Sales, SalesItem
from django.dispatch import receiver
from .invoice_generator import generate_invoice_pdf


@receiver(post_save, sender=Sales)
def send_invoice_email(sender, instance, created, **kwargs):
    if created:
        customer_email = instance.customer.email
        subject = f"invoice for sale {instance.id}"
        message = f"""
        Dear {instance.customer.name},
        
        Thank you for your purchase!
        
        Invoice Details:
        Sale ID: {instance.id}
        Date: 
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
                    # to=list(admin_emails),
                    #   # Send to all admins
                    to=["anuzb50@gmail.com"],
                )
                email.send(fail_silently=False)
                print(f"Low stock email sent for {product.name}")
