from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("manager", "Manager"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
