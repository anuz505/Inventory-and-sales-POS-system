from rest_framework import serializers
from .models import User


class UserSerailizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "date_joined",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined"]
