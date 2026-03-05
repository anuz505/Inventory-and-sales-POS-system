from datetime import timedelta
from django.utils import timezone

from django.conf import settings
from django.core.mail import EmailMessage
from celery import shared_task
from users.models import PasswordResetOTP
import random
from users.models import User


def generate_otp():
    return str(random.randint(100000, 999999))


@shared_task
def send_otp_via_email(user_id):
    user = User.objects.get(pk=user_id)
    otp: str = generate_otp()
    subject = "Your Password Reset OTP"
    message = f"""
            Hello {user.first_name},

            Your password reset OTP is: {otp}

            This code will expire in 10 minutes.

            If you didn't request a password reset, please ignore this email.

            Best regards,
            The Support Team
            {user.email}
            {otp}
            """
    PasswordResetOTP.objects.create(
        user=user, otp=otp, expired_at=timezone.now() + timedelta(minutes=10)
    )
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.send(fail_silently=False)
