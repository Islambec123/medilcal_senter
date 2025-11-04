from django.core.mail import send_mail
from django.conf import settings
import random

def send_otp_email(user_email, subject="Your OTP Code"):
    otp = random.randint(100000, 999999)  # 6-значный код
    message = f"Your OTP code is: {otp}"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return otp