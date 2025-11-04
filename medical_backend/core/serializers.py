# core/serializers.py
from rest_framework import serializers
import ipaddress
from .models import (
    Section, SectionImage, SystemSetting, AuditLog, ActivityLog,
    Specialization, Doctor, Schedule, DoctorReview
)


class SectionImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionImage
        fields = ['id', 'image', 'image_url', 'caption', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class SectionSerializer(serializers.ModelSerializer):
    images = SectionImageSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id', 'section_type', 'title', 'subtitle', 'description',
            'content', 'image', 'image_url', 'background_image', 'background_image_url',
            'is_active', 'display_order', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_background_image_url(self, obj):
        if obj.background_image:
            return obj.background_image.url
        return None


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['section_type', 'title', 'subtitle', 'description', 'content',
                  'image', 'background_image', 'is_active', 'display_order']


class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = ['id', 'key', 'value', 'description', 'data_type', 'is_public',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'user_id', 'user_email', 'action', 'resource_type',
                  'resource_id', 'details', 'ip_address', 'created_at']  # 👈 Добавляем ip_address обратно
        read_only_fields = fields


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user_id', 'user_email', 'activity_type', 'description',
                  'metadata', 'created_at']
        read_only_fields = fields


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'icon', 'created_at']
        read_only_fields = ['id', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'is_working']
        read_only_fields = ['id']


class DoctorReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = DoctorReview
        fields = ['id', 'patient', 'patient_name', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'created_at']


class DoctorListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка врачей"""
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    photo_url = serializers.SerializerMethodField()
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'user_full_name', 'specialization', 'specialization_name',
            'experience_years', 'photo', 'photo_url', 'rating', 'review_count',
            'consultation_fee', 'is_available', 'is_verified'
        ]
        read_only_fields = ['id']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class DoctorDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о враче"""
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    photo_url = serializers.SerializerMethodField()
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    reviews = DoctorReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'user_full_name', 'user_email', 'specialization', 'specialization_name',
            'license_number', 'experience_years', 'education', 'bio', 'phone',
            'office_number', 'photo', 'photo_url', 'certificate', 'consultation_fee',
            'is_available', 'is_verified', 'rating', 'review_count', 'schedules', 'reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class DoctorReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзывов"""

    class Meta:
        model = DoctorReview
        fields = ['doctor', 'patient', 'rating', 'comment']


class ScheduleDetailSerializer(serializers.ModelSerializer):
    """Сериализатор расписания с информацией о враче"""
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    specialization = serializers.CharField(source='doctor.specialization.name', read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'doctor_name', 'specialization', 'day_of_week',
                  'start_time', 'end_time', 'is_working']
        read_only_fields = ['id']


class IPAddressField(serializers.CharField):
    """Кастомное поле для IP-адреса"""

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            # Валидация IP-адреса
            ipaddress.ip_address(value)
            return value
        except ValueError:
            raise serializers.ValidationError("Invalid IP address format")

    def to_representation(self, value):
        return str(value) if value else None


class AuditLogSerializer(serializers.ModelSerializer):
    # Используем кастомное поле для IP-адреса
    ip_address = IPAddressField(required=False, allow_null=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user_id', 'user_email', 'action', 'resource_type',
                  'resource_id', 'details', 'ip_address', 'created_at']
        read_only_fields = fields


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user_id', 'user_email', 'activity_type', 'description',
                  'metadata', 'created_at']
        read_only_fields = fields