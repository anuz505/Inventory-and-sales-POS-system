from django.core.mail import EmailMessage
from users.models import User
from django.db.models.signals import post_save
from .models import Sales
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
            from_email=instance.user.email,
            to=[customer_email],
        )
        email.attach(
            f"invoice_{instance.invoice_number}.pdf",
            pdf_buffer.getvalue(),
            "application/pdf",
        )
        email.send(fail_silently=False)
