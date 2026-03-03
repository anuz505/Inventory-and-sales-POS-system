from django.core.mail import EmailMessage
from django.conf import settings
from users.models import User
from .models import Customer, Sales, SalesItem
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.cache import cache
from .tasks import send_invoice_email_manually, send_low_stock_email
from django.db import transaction


@receiver(post_save, sender=Sales)
def send_invoice_email(sender, instance, created, **kwargs):
    if created and instance.payment_status == "completed":
        transaction.on_commit(lambda: send_invoice_email_manually.delay(instance.id))
        return
    if getattr(instance, "_send_invoice_email", False):
        transaction.on_commit(lambda: send_invoice_email_manually.delay(instance.id))


@receiver(post_save, sender=SalesItem)
def send_low_stock_notification(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: send_low_stock_email.delay(instance.product.id))


@receiver([post_save, post_delete], sender=Customer)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete_pattern("*customers*")
