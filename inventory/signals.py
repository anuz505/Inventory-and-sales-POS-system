from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Category, Product, Supplier


@receiver([post_save, post_delete], sender=Category)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete_pattern("*categories*")


@receiver([post_save, post_delete], sender=Product)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete_pattern("*products*")


@receiver([post_save, post_delete], sender=Supplier)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete_pattern("*suppliers*")
