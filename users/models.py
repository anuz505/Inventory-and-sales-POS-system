from django.utils import timezone

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("manager", "Manager"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="staff")
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class PasswordResetOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expired_at
