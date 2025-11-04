from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Кастомная схема с группами
schema_view = get_schema_view(
    openapi.Info(
        title="Medical System API",
        default_version='v1',
        description="API для медицинской системы",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@medical.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[],  # Будет заполнено автоматически
)

# Кастомные теги для группировки
SWAGGER_TAGS = [
    {
        'name': 'Sections',
        'description': 'Управление секциями главной страницы'
    },
    {
        'name': 'System Settings',
        'description': 'Управление системными настройками'
    },
    {
        'name': 'Logs',
        'description': 'Просмотр логов системы'
    },
    {
        'name': 'Doctors Management',
        'description': 'Управление врачами, расписанием и отзывами'
    },
    {
        'name': 'Public API',
        'description': 'Публичные endpoints для клиентов'
    }
]