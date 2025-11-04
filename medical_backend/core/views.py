# core/views.py
import logging
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .filters import DoctorFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Section, SectionImage, SystemSetting, AuditLog, ActivityLog,
    Specialization, Doctor, Schedule, DoctorReview
)
from .serializers import (
    SectionSerializer, SectionCreateSerializer, SectionImageSerializer,
    SystemSettingSerializer, AuditLogSerializer, ActivityLogSerializer,
    SpecializationSerializer, DoctorListSerializer, DoctorDetailSerializer,
    ScheduleSerializer, DoctorReviewSerializer, DoctorReviewCreateSerializer
)
from .permissions import IsManager

logger = logging.getLogger(__name__)

# ==================== SECTIONS ====================

@swagger_auto_schema(tags=['Sections'])
class SectionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления секциями главной страницы"""
    """ViewSet для управления секциями"""
    permission_classes = [IsManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'subtitle', 'description']
    filterset_fields = ['section_type', 'is_active']
    ordering_fields = ['display_order', 'created_at']
    ordering = ['display_order']

    def get_queryset(self):
        return Section.objects.all().prefetch_related('images')

    def get_serializer_class(self):
        if self.action == 'create':
            return SectionCreateSerializer
        return SectionSerializer

    def perform_create(self, serializer):
        # Сохраняем пользователя для сигналов
        instance = serializer.save()
        instance._current_user = self.request.user
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance._current_user = self.request.user
        instance.save()

    @swagger_auto_schema(
        operation_description="Активировать/деактивировать секцию",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
        )
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Активировать/деактивировать секцию"""
        section = self.get_object()
        section.is_active = not section.is_active
        section._current_user = request.user
        section.save()

        action = 'activated' if section.is_active else 'deactivated'
        return Response({
            'message': f'Section {action} successfully',
            'is_active': section.is_active
        })

    @swagger_auto_schema(
        operation_description="Изменить порядок секций",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_order': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Изменить порядок секции"""
        section = self.get_object()
        new_order = request.data.get('new_order')

        if new_order is None:
            return Response({'error': 'new_order is required'}, status=400)

        section.display_order = new_order
        section._current_user = request.user
        section.save()

        return Response({
            'message': 'Section order updated successfully',
            'display_order': section.display_order
        })

@swagger_auto_schema(tags=['Sections'])
class SectionImageViewSet(viewsets.ModelViewSet):
    """ViewSet для управления изображениями секций"""
    """ViewSet для управления изображениями секций"""
    permission_classes = [IsManager]
    serializer_class = SectionImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['section__section_type']
    ordering_fields = ['order']
    ordering = ['order']

    def get_queryset(self):
        return SectionImage.objects.all().select_related('section')

    def perform_create(self, serializer):
        instance = serializer.save()
        instance._current_user = self.request.user

    def perform_update(self, serializer):
        instance = serializer.save()
        instance._current_user = self.request.user

# ==================== SYSTEM SETTINGS ====================

@swagger_auto_schema(tags=['System Settings'])
class SystemSettingViewSet(viewsets.ModelViewSet):
    """ViewSet для управления системными настройками"""
    """ViewSet для управления системными настройками"""
    permission_classes = [IsManager]
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    filter_backends = [SearchFilter]
    search_fields = ['key', 'description']

    @swagger_auto_schema(
        operation_description="Получить настройку по ключу",
        responses={200: SystemSettingSerializer}
    )
    @action(detail=False, methods=['get'], url_path='by-key/(?P<key>[^/.]+)')
    def by_key(self, request, key=None):
        """Получить настройку по ключу"""
        try:
            setting = SystemSetting.objects.get(key=key)
            serializer = self.get_serializer(setting)
            return Response(serializer.data)
        except SystemSetting.DoesNotExist:
            return Response(
                {'error': f'Setting with key "{key}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )

# ==================== LOGS ====================

@swagger_auto_schema(tags=['Logs'])
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра логов аудита"""
    permission_classes = [IsManager]
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'user_email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.all()


@swagger_auto_schema(tags=['Logs'])
class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра логов активности"""
    permission_classes = [IsManager]
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['activity_type', 'user_email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return ActivityLog.objects.all()

# ==================== DOCTORS MANAGEMENT ====================

@swagger_auto_schema(tags=['Doctors Management'])
class SpecializationViewSet(viewsets.ModelViewSet):
    """ViewSet для специализаций"""
    permission_classes = [IsManager]
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public_list(self, request):
        """Публичный список специализаций"""
        specializations = Specialization.objects.all()
        serializer = self.get_serializer(specializations, many=True)
        return Response(serializer.data)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@swagger_auto_schema(tags=['Doctors Management'])
class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet для врачей"""
    permission_classes = [IsManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DoctorFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['user__full_name', 'specialization__name', 'bio']
    filterset_fields = ['specialization', 'is_available', 'is_verified']
    ordering_fields = ['rating', 'experience_years', 'consultation_fee', 'created_at']
    ordering = ['-rating']

    def get_queryset(self):
        return Doctor.objects.all().select_related('user', 'specialization').prefetch_related('schedules', 'reviews')

    def get_serializer_class(self):
        if self.action == 'list':
            return DoctorListSerializer
        return DoctorDetailSerializer

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public_list(self, request):
        """Публичный список врачей (доступен всем)"""
        doctors = Doctor.objects.filter(
            is_available=True,
            is_verified=True
        ).select_related('user', 'specialization')

        # Фильтрация для публичного API
        specialization = request.query_params.get('specialization')
        if specialization:
            doctors = doctors.filter(specialization_id=specialization)

        serializer = DoctorListSerializer(doctors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public_detail(self, request, pk=None):
        """Публичная детальная информация о враче (доступна всем)"""
        try:
            doctor = Doctor.objects.get(
                id=pk,
                is_available=True,
                is_verified=True
            )
            serializer = DoctorDetailSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)

    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Переключить доступность врача"""
        doctor = self.get_object()
        doctor.is_available = not doctor.is_available
        doctor.save()

        return Response({
            'message': f'Doctor availability set to {doctor.is_available}',
            'is_available': doctor.is_available
        })

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Верифицировать врача"""
        doctor = self.get_object()
        doctor.is_verified = True
        doctor.save()

        return Response({
            'message': 'Doctor verified successfully',
            'is_verified': doctor.is_verified
        })


@swagger_auto_schema(tags=['Doctors Management'])
class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet для расписания"""
    permission_classes = [IsManager]
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'day_of_week', 'is_working']

    def get_queryset(self):
        return Schedule.objects.all().select_related('doctor')

    @action(detail=False, methods=['get'])
    def doctor_schedule(self, request):
        """Получить расписание конкретного врача"""
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({'error': 'doctor_id is required'}, status=400)

        schedules = Schedule.objects.filter(doctor_id=doctor_id, is_working=True)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available_slots(self, request):
        """Получить доступные слоты для записи (публичный)"""
        doctor_id = request.query_params.get('doctor_id')
        date = request.query_params.get('date')

        # Здесь можно добавить логику расчета доступных слотов
        return Response({'message': 'Available slots endpoint'})


@swagger_auto_schema(tags=['Doctors Management'])
class DoctorReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов о врачах"""
    permission_classes = [IsManager]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'is_approved']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return DoctorReview.objects.all().select_related('doctor', 'patient')

    def get_serializer_class(self):
        if self.action == 'create':
            return DoctorReviewCreateSerializer
        return DoctorReviewSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Одобрить отзыв"""
        review = self.get_object()
        review.is_approved = True
        review.save()

        return Response({
            'message': 'Review approved successfully',
            'is_approved': review.is_approved
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить отзыв"""
        review = self.get_object()
        review.is_approved = False
        review.save()

        return Response({
            'message': 'Review rejected',
            'is_approved': review.is_approved
        })

# ==================== PUBLIC API ====================
class PublicDoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """Публичный API для получения информации о врачах"""
    permission_classes = [AllowAny]
    serializer_class = DoctorListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DoctorFilter
    search_fields = ['user__full_name', 'specialization__name']
    ordering_fields = ['rating', 'experience_years']
    ordering = ['-rating']

    def get_queryset(self):
        return Doctor.objects.filter(
            is_available=True,
            is_verified=True
        ).select_related('user', 'specialization')

    @swagger_auto_schema(tags=['Public API'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Public API'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class PublicSpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """Публичный API для получения специализаций"""
    permission_classes = [AllowAny]
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer

    @swagger_auto_schema(tags=['Public API'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Public API'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)