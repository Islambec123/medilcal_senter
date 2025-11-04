# core/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import (
    Section, SectionImage, SystemSetting, AuditLog, ActivityLog,
    Specialization, Doctor, Schedule, DoctorReview, Appointment,
    MedicalRecord, Service, Patient, TimeSlot, Prescription,
    Clinic, Department, DoctorClinic, Payment, Notification
)

User = get_user_model()


# === INLINE MODELS ===
class SectionImageInline(admin.TabularInline):
    model = SectionImage
    extra = 1
    fields = ['image', 'preview_image', 'caption', 'order']
    readonly_fields = ['preview_image']

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "—"
    preview_image.short_description = 'Preview'


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 7
    fields = ['day_of_week', 'start_time', 'end_time', 'is_working']
    ordering = ['day_of_week']


class DoctorReviewInline(admin.TabularInline):
    model = DoctorReview
    extra = 0
    fields = ['patient', 'rating', 'comment', 'is_approved', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('doctor', 'patient', 'doctor__user')
        if request.user.role == 'manager':
            # Исправленная логика для менеджера
            return qs.filter(doctor__user=request.user)
        return qs


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 0
    fields = ['date', 'start_time', 'end_time', 'is_available', 'appointment_link']
    readonly_fields = ['appointment_link']
    ordering = ['date', 'start_time']

    def appointment_link(self, obj):
        if obj.appointment:
            url = reverse('admin:core_appointment_change', args=[obj.appointment.id])
            return format_html('<a href="{}">📅 {}</a>', url, obj.appointment)
        return "—"
    appointment_link.short_description = 'Запись'


class DoctorClinicInline(admin.TabularInline):
    model = DoctorClinic
    extra = 1
    fields = ['clinic', 'department', 'is_active']
    ordering = ['clinic']


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0
    fields = ['medication_name', 'dosage', 'is_active', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# === SECTION ADMIN ===
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['section_type', 'title', 'is_active', 'display_order', 'preview_image']
    list_editable = ['is_active', 'display_order']
    list_filter = ['section_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['created_at', 'updated_at', 'preview_image']
    actions = ['activate_sections', 'deactivate_sections']
    inlines = [SectionImageInline]
    ordering = ['display_order']

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover;" />', obj.image.url)
        return "—"
    preview_image.short_description = 'Preview'

    def activate_sections(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано {updated} секций', messages.SUCCESS)
    activate_sections.short_description = "✅ Активировать секции"

    def deactivate_sections(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🚫 Деактивировано {updated} секций', messages.WARNING)
    deactivate_sections.short_description = "🚫 Деактивировать секции"


@admin.register(SectionImage)
class SectionImageAdmin(admin.ModelAdmin):
    list_display = ['section', 'caption', 'order', 'preview_image']
    list_editable = ['order']
    list_filter = ['section__section_type', 'created_at']
    search_fields = ['caption', 'section__title']
    readonly_fields = ['preview_image', 'created_at', 'updated_at']

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "—"
    preview_image.short_description = 'Preview'


# === SYSTEM SETTINGS ADMIN ===
@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'data_type', 'is_public', 'created_at']
    list_editable = ['value', 'is_public']
    list_filter = ['data_type', 'is_public', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['key']
    actions = ['make_public', 'make_private']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'manager':
            return qs.filter(is_public=True)
        return qs

    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'🌐 Сделано публичными {updated} настроек', messages.SUCCESS)
    make_public.short_description = "🌐 Сделать публичными"

    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'🔒 Сделано приватными {updated} настроек', messages.WARNING)
    make_private.short_description = "🔒 Сделать приватными"


# === LOGS ADMIN ===
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'action', 'resource_type', 'resource_id', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user_email', 'resource_type']
    readonly_fields = ['user_id', 'user_email', 'action', 'resource_type', 'resource_id', 'details', 'ip_address', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user_email', 'activity_type', 'description']
    readonly_fields = ['user_id', 'user_email', 'activity_type', 'description', 'metadata', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False


# === CLINIC MANAGEMENT ===
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'doctors_count', 'appointments_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'doctors_count', 'appointments_count']
    list_editable = ['is_active']
    inlines = [DoctorClinicInline]
    actions = ['activate_clinics', 'deactivate_clinics']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('doctors__doctor', 'appointments')

    def doctors_count(self, obj):
        return obj.doctors.count()
    doctors_count.short_description = 'Врачей'

    def appointments_count(self, obj):
        return obj.appointments.count()
    appointments_count.short_description = 'Записей'

    def activate_clinics(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано {updated} клиник', messages.SUCCESS)
    activate_clinics.short_description = "✅ Активировать клиники"

    def deactivate_clinics(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🚫 Деактивировано {updated} клиник', messages.WARNING)
    deactivate_clinics.short_description = "🚫 Деактивировать клиники"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic', 'head_doctor_name', 'doctors_count']
    list_filter = ['clinic', 'created_at']
    search_fields = ['name', 'clinic__name', 'head_doctor__user__full_name']
    readonly_fields = ['created_at', 'updated_at', 'doctors_count']

    def head_doctor_name(self, obj):
        return obj.head_doctor.user.full_name if obj.head_doctor else "—"
    head_doctor_name.short_description = 'Главный врач'

    def doctors_count(self, obj):
        return obj.doctorclinic_set.count()
    doctors_count.short_description = 'Врачей в отделении'


# === DOCTORS MANAGEMENT ===
@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'doctors_count', 'active_doctors_count', 'created_at']
    list_editable = ['icon']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'doctors_count', 'active_doctors_count']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('doctors')

    def doctors_count(self, obj):
        return obj.doctors.count()
    doctors_count.short_description = 'Всего врачей'

    def active_doctors_count(self, obj):
        return obj.doctors.filter(is_available=True).count()
    active_doctors_count.short_description = 'Активных врачей'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        'user_full_name', 'specialization', 'experience_years', 'average_rating',
        'reviews_count', 'is_available', 'is_verified', 'preview_photo', 'user_profile_link'
    ]
    list_editable = ['is_available', 'is_verified']
    list_filter = ['specialization', 'is_available', 'is_verified', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'specialization__name', 'user__doctorprofile__license_number']
    readonly_fields = ['created_at', 'updated_at', 'preview_photo', 'average_rating', 'reviews_count', 'user_profile_link']
    actions = ['activate_doctors', 'deactivate_doctors', 'verify_doctors', 'unverify_doctors']
    inlines = [ScheduleInline, DoctorReviewInline, TimeSlotInline, DoctorClinicInline]
    ordering = ['user__full_name']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('user', 'specialization').prefetch_related('reviews__patient')
        if request.user.is_superuser:
            return qs
        if request.user.role == 'manager':
            # Простая фильтрация по пользователю
            return qs.filter(user=request.user)
        return qs

    def user_full_name(self, obj):
        return obj.user.full_name
    user_full_name.short_description = 'ФИО'

    def preview_photo(self, obj):
        if hasattr(obj.user, 'doctorprofile') and obj.user.doctorprofile.photo:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />',
                obj.user.doctorprofile.photo.url
            )
        return "—"
    preview_photo.short_description = 'Фото'

    def average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return f"{avg:.1f}" if avg else "Нет отзывов"
    average_rating.short_description = 'Средний рейтинг'

    def reviews_count(self, obj):
        return obj.reviews.count()
    reviews_count.short_description = 'Количество отзывов'

    def user_profile_link(self, obj):
        try:
            # Попробуйте один из этих вариантов:
            url = reverse('admin:user_user_change', args=[obj.user.id])
            # ИЛИ
            # url = reverse('admin:auth_user_change', args=[obj.user.id])
            # ИЛИ
            # url = reverse('admin:user_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">👤 Редактировать профиль пользователя</a>', url)
        except:
            return format_html(f"👤 {obj.user.email}")

    def activate_doctors(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'✅ Активировано {updated} врачей', messages.SUCCESS)
    activate_doctors.short_description = "✅ Активировать врачей"

    def deactivate_doctors(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'🚫 Деактивировано {updated} врачей', messages.WARNING)
    deactivate_doctors.short_description = "🚫 Деактивировать врачей"

    def verify_doctors(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'✅ Верифицировано {updated} врачей', messages.SUCCESS)
    verify_doctors.short_description = "✅ Верифицировать врачей"

    def unverify_doctors(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'❌ Снята верификация с {updated} врачей', messages.WARNING)
    unverify_doctors.short_description = "❌ Снять верификацию"


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_working']
    list_editable = ['is_working']
    list_filter = ['doctor', 'day_of_week', 'is_working']
    search_fields = ['doctor__user__full_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['doctor', 'day_of_week']
    actions = ['activate_schedules', 'deactivate_schedules']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('doctor__user')
        if request.user.role == 'manager':
            return qs.filter(doctor__user=request.user)
        return qs

    def activate_schedules(self, request, queryset):
        updated = queryset.update(is_working=True)
        self.message_user(request, f'✅ Активировано {updated} расписаний', messages.SUCCESS)
    activate_schedules.short_description = "✅ Активировать расписания"

    def deactivate_schedules(self, request, queryset):
        updated = queryset.update(is_working=False)
        self.message_user(request, f'🚫 Деактивировано {updated} расписаний', messages.WARNING)
    deactivate_schedules.short_description = "🚫 Деактивировать расписания"


# === APPOINTMENTS & TIME SLOTS ===
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'is_available', 'appointment_link']
    list_filter = ['doctor', 'date', 'is_available']
    search_fields = ['doctor__user__full_name', 'date']
    readonly_fields = ['created_at', 'updated_at', 'appointment_link']
    actions = ['make_available', 'make_unavailable']
    ordering = ['-date', 'start_time']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('doctor__user', 'appointment__patient')
        if request.user.role == 'manager':
            return qs.filter(doctor__user=request.user)
        return qs

    def appointment_link(self, obj):
        if obj.appointment:
            url = reverse('admin:core_appointment_change', args=[obj.appointment.id])
            return format_html('<a href="{}">📅 {}</a>', url, obj.appointment)
        return "—"
    appointment_link.short_description = 'Запись'

    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'✅ Освобождено {updated} слотов', messages.SUCCESS)
    make_available.short_description = "✅ Освободить слоты"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'🚫 Заблокировано {updated} слотов', messages.WARNING)
    make_unavailable.short_description = "🚫 Заблокировать слоты"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'date', 'time', 'status', 'service', 'patient_profile_link']
    list_filter = ['doctor', 'date', 'status', 'service', 'clinic']
    search_fields = ['doctor__user__full_name', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['created_at', 'updated_at', 'patient_profile_link']
    actions = ['mark_completed', 'mark_cancelled', 'mark_confirmed']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'doctor__user', 'patient', 'service', 'clinic', 'time_slot'
        )
        if request.user.role == 'manager':
            return qs.filter(doctor__user=request.user)
        return qs

    def patient_profile_link(self, obj):
        url = reverse('admin:core_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">👤 Профиль пациента</a>', url)
    patient_profile_link.short_description = 'Профиль'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'✅ Отмечено как завершено: {updated} записей', messages.SUCCESS)
    mark_completed.short_description = "✅ Отметить завершенными"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'❌ Отменено {updated} записей', messages.WARNING)
    mark_cancelled.short_description = "❌ Отменить записи"

    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'✅ Подтверждено {updated} записей', messages.SUCCESS)
    mark_confirmed.short_description = "✅ Подтвердить записи"


# === PATIENTS & MEDICAL RECORDS ===
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'gender', 'appointments_count']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_filter = ['gender', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'appointments_count']
    inlines = [PrescriptionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('appointments')
        if request.user.role == 'manager':
            return qs.filter(appointments__doctor__user=request.user).distinct()
        return qs

    def appointments_count(self, obj):
        return obj.appointments.count()
    appointments_count.short_description = 'Количество записей'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__user__full_name']
    readonly_fields = ['created_at', 'updated_at', 'files']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('patient', 'doctor__user', 'appointment')
        if request.user.role == 'manager':
            return qs.filter(doctor__user=request.user)
        return qs


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'medication_name', 'dosage', 'is_active', 'created_at']
    list_filter = ['is_active', 'doctor', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'medication_name', 'doctor__user__full_name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    actions = ['activate_prescriptions', 'deactivate_prescriptions']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('patient', 'doctor__user', 'appointment')
        if request.user.role == 'manager':
            return qs.filter(doctor__user=request.user)
        return qs

    def activate_prescriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано {updated} рецептов', messages.SUCCESS)
    activate_prescriptions.short_description = "✅ Активировать рецепты"

    def deactivate_prescriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🚫 Деактивировано {updated} рецептов', messages.WARNING)
    deactivate_prescriptions.short_description = "🚫 Деактивировать рецепты"


# === SERVICES & REVIEWS ===
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'price', 'duration_minutes', 'is_active']
    list_filter = ['specialization', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    actions = ['activate_services', 'deactivate_services']

    def activate_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано {updated} услуг', messages.SUCCESS)
    activate_services.short_description = "✅ Активировать услуги"

    def deactivate_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🚫 Деактивировано {updated} услуг', messages.WARNING)
    deactivate_services.short_description = "🚫 Деактивировать услуги"


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'rating', 'is_approved', 'would_recommend', 'created_at']
    list_editable = ['is_approved']
    list_filter = ['doctor', 'is_approved', 'rating', 'would_recommend', 'created_at']
    search_fields = ['doctor__user__full_name', 'patient__first_name', 'patient__last_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    actions = ['approve_reviews', 'reject_reviews']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('doctor__user', 'patient', 'appointment')
        if request.user.role == 'manager':
            # Исправленная логика - фильтруем по пользователю врача
            return qs.filter(doctor__user=request.user)
        return qs

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'✅ Одобрено {updated} отзывов', messages.SUCCESS)
    approve_reviews.short_description = "✅ Одобрить отзывы"

    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'❌ Отклонено {updated} отзывов', messages.WARNING)
    reject_reviews.short_description = "❌ Отклонить отзывы"


# === PAYMENTS & NOTIFICATIONS ===
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'appointment', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_completed', 'mark_failed']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('patient', 'appointment__doctor__user')
        if request.user.role == 'manager':
            return qs.filter(appointment__doctor__user=request.user)
        return qs

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'✅ Отмечено как оплачено: {updated} платежей', messages.SUCCESS)
    mark_completed.short_description = "✅ Отметить оплаченными"

    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'❌ Отмечено как неудачные: {updated} платежей', messages.WARNING)
    mark_failed.short_description = "❌ Отметить неудачными"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'✅ Отмечено как прочитано: {updated} уведомлений', messages.SUCCESS)
    mark_as_read.short_description = "✅ Отметить прочитанными"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'🔄 Отмечено как непрочитано: {updated} уведомлений', messages.INFO)
    mark_as_unread.short_description = "🔄 Отметить непрочитанными"