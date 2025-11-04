from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import *

router = DefaultRouter()

# Sections
router.register(r'sections', SectionViewSet, basename='sections')
router.register(r'section-images', SectionImageViewSet, basename='section-images')

# System Settings
router.register(r'settings', SystemSettingViewSet, basename='system-settings')

# Logs
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-logs')

# Doctors Management
router.register(r'specializations', SpecializationViewSet, basename='specializations')
router.register(r'doctors', DoctorViewSet, basename='doctors')
router.register(r'schedules', ScheduleViewSet, basename='schedules')
router.register(r'doctor-reviews', DoctorReviewViewSet, basename='doctor-reviews')

# Public API
router.register(r'public/doctors', PublicDoctorViewSet, basename='public-doctors')
router.register(r'public/specializations', PublicSpecializationViewSet, basename='public-specializations')

# Кастомная схема Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Medical System API",
        default_version='v1',
        description="API для медицинской системы с логической группировкой endpoints",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@medical.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),

    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]