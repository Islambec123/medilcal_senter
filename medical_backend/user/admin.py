# core/admin.py (или в account/admin.py, если модель там)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Что отображается в списке
    list_display = (
        'username', 'email', 'full_name', 'role',
        'is_email_verified', 'is_staff', 'is_active', 'is_superuser'
    )

    # Фильтры
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_active', 'is_superuser')

    # Поля для поиска
    search_fields = ('username', 'email', 'full_name')

    # Сортировка
    ordering = ('email',)

    # Поля в форме редактирования пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('full_name', 'role', 'phone_number')}),
        ('Verification', {'fields': ('is_email_verified', 'verification_code', 'verification_code_created_at', 'otp', 'otp_created_at')}),
    )

    # Поля при создании пользователя через админку
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': (
                'username', 'email', 'full_name', 'password1', 'password2',
                'role', 'is_email_verified'
            ),
        }),
    )