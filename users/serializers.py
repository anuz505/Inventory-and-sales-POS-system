from rest_framework import serializers
from .models import PasswordResetOTP, User
from django.contrib.auth import authenticate
from django.utils import timezone


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
            "is_staff",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=255,
        error_messages={
            "required": "Email is required.",
            "invalid": "Please provide a valid email address.",
        },
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={
            "min_length": "Password must be at least 8 characters long."
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone_number",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate_new_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one number.")
        if not any(char.isupper() for char in value):
            errors.append(
                "Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in value):
            errors.append(
                "Password must contain at least one lowercase letter."
            )
        if not any(not char.isalnum() for char in value):
            errors.append(
                "Password must contain at least one special character."
            )
        if errors:
            raise serializers.ValidationError(errors)
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )
        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid username or password."]}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["User account is disabled."]}
            )
        data["user"] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """For changing password"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("old password is incorrect")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        errors = []
        if not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one number.")
        if not any(char.isupper() for char in value):
            errors.append(
                "Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in value):
            errors.append(
                "Password must contain at least one lowercase letter."
            )
        if not any(not char.isalnum() for char in value):
            errors.append(
                "Password must contain at least one special character."
            )
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No user found with this email."}
            )

        otp_record = (
            PasswordResetOTP.objects.filter(user=user, otp=data["otp"])
            .order_by("-created_at")
            .first()
        )

        if not otp_record:
            raise serializers.ValidationError({"otp": "Invalid OTP."})
        if otp_record.expired_at < timezone.now():
            raise serializers.ValidationError({"otp": "OTP has expired."})

        data["user"] = user
        data["otp_record"] = otp_record
        return data

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        self.validated_data["otp_record"].delete()
