# core/models.py (или в одном из приложений, например account)
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random

class CustomUser(AbstractUser):
    # Основные поля
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True)

    # Верификация email
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(blank=True, null=True)

    # OTP (для одноразовых паролей)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    # Роли
    ROLES = (
        ('client', 'Client'),
        ('doctor', 'Doctor'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='client')

    # Поля для AbstractUser
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"

    # OTP
    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp', 'otp_created_at'])
        return self.otp

    def verify_otp(self, otp):
        if self.otp != otp:
            return False
        if self.otp_created_at and timezone.now() > self.otp_created_at + timezone.timedelta(minutes=5):
            return False
        self.otp = None
        self.otp_created_at = None
        self.save(update_fields=['otp', 'otp_created_at'])
        return True

    # Email verification
    def generate_verification_code(self):
        self.verification_code = f"{random.randint(100000, 999999)}"
        self.verification_code_created_at = timezone.now()
        self.save(update_fields=['verification_code', 'verification_code_created_at'])
        return self.verification_code

    def verify_email(self, code):
        if self.verification_code != code:
            return False
        if self.verification_code_created_at and timezone.now() > self.verification_code_created_at + timezone.timedelta(minutes=10):
            return False
        self.is_email_verified = True
        self.verification_code = None
        self.verification_code_created_at = None
        self.save(update_fields=['is_email_verified', 'verification_code', 'verification_code_created_at'])
        return True


class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)  # 6-значный код
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f'{self.email} - {self.code}'