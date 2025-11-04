# core/models.py
from django.db.models import Avg
from django.db import models
from django.utils import timezone
from django.conf import settings

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

class DoctorProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255, blank=True)

class ClientProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField(blank=True)

class ManagerProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.CharField(max_length=255, blank=True)

class BaseModel(models.Model):
    """Абстрактная базовая модель"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Section(BaseModel):
    """Модель для секций главной страницы"""

    SECTION_TYPES = [
        ('hero', '🎯 Hero Section'),
        ('features', '✨ Features'),
        ('services', '🛠️ Services'),
        ('about', '👥 About Us'),
        ('testimonials', '💬 Testimonials'),
        ('contact', '📞 Contact'),
    ]

    section_type = models.CharField(max_length=50, choices=SECTION_TYPES, unique=True)
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    content = models.JSONField(default=dict, blank=True)

    # Медиа
    image = models.ImageField(upload_to='sections/', blank=True, null=True)
    background_image = models.ImageField(upload_to='sections/bg/', blank=True, null=True)

    # Настройки
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'core_sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['display_order']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"


class SectionImage(BaseModel):
    """Изображения для секций"""

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='section_images/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'core_section_images'
        ordering = ['order']

    def __str__(self):
        return f"{self.section.section_type} - {self.caption or 'Image'}"


class SystemSetting(BaseModel):
    """Системные настройки"""

    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    data_type = models.CharField(
        max_length=20,
        choices=[('string', 'String'), ('integer', 'Integer'), ('boolean', 'Boolean'), ('json', 'JSON')],
        default='string'
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"{self.key} = {self.value}"


class AuditLog(BaseModel):
    """Логи аудита для действий менеджеров"""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('toggle', 'Toggle'),
        ('reorder', 'Reorder'),
    ]

    user_id = models.IntegerField()
    user_email = models.EmailField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.IntegerField(null=True, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True, protocol='both')

    class Meta:
        db_table = 'core_audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_email} - {self.action} - {self.resource_type}"


class ActivityLog(BaseModel):
    """Логи активности"""

    user_id = models.IntegerField()
    user_email = models.EmailField()
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'core_activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_email} - {self.activity_type}"


class Specialization(BaseModel):
    """Специализации врачей"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Иконка FontAwesome")

    class Meta:
        db_table = 'core_specializations'
        verbose_name = 'Specialization'
        verbose_name_plural = 'Specializations'

    def __str__(self):
        return self.name


class Clinic(BaseModel):
    """Клиника или медицинский центр"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    working_hours = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_clinics'
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'

    def __str__(self):
        return self.name


class Department(BaseModel):
    """Отделения клиники"""
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    head_doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'core_departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"


class Doctor(BaseModel):
    """Модель врача"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ForeignKey(Specialization, on_delete=models.PROTECT, related_name='doctors')

    # Основная информация
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(default=0)
    education = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    # Контактная информация
    phone = models.CharField(max_length=20, blank=True)
    office_number = models.CharField(max_length=10, blank=True)

    # Медиа
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)

    # Рабочие параметры
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    review_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # Рейтинги и статистика
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        db_table = 'core_doctors'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['-rating', 'user__full_name']

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.specialization.name}"

    @property
    def average_rating(self):
        """Вычисляемый средний рейтинг"""
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 2) if avg else 0.0

    def update_review_stats(self):
        """Обновление статистики отзывов"""
        self.rating = self.average_rating
        self.review_count = self.reviews.count()
        self.save(update_fields=['rating', 'review_count'])


class DoctorClinic(BaseModel):
    """Связь врача с клиникой и отделением"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='clinics')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_doctor_clinics'
        verbose_name = 'Doctor Clinic'
        verbose_name_plural = 'Doctor Clinics'
        unique_together = ['doctor', 'clinic']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.clinic.name}"


class Schedule(BaseModel):
    """Расписание врача"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.PositiveSmallIntegerField(
        choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
                 (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_schedules'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        unique_together = ['doctor', 'day_of_week']
        ordering = ['doctor', 'day_of_week']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.get_day_of_week_display()}"


class Service(BaseModel):
    """Медицинские услуги"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)
    specialization = models.ForeignKey(
        Specialization, on_delete=models.SET_NULL, null=True, blank=True, related_name='services'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']

    def __str__(self):
        return self.name


class Patient(BaseModel):
    """Модель для пациентов"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        default='other'
    )
    address = models.TextField(blank=True)

    class Meta:
        db_table = 'core_patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class TimeSlot(BaseModel):
    """Временные слоты для записи"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        # related_name='time_slot'
    )

    class Meta:
        db_table = 'core_time_slots'
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.date} {self.start_time}"


class Appointment(BaseModel):
    """Модель для записи пациента к врачу"""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)

    date = models.DateField()
    time = models.TimeField()
    time_slot = models.OneToOneField(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_appointment'
    )

    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    # Новые поля
    duration_minutes = models.PositiveIntegerField(default=30)
    is_urgent = models.BooleanField(default=False)
    symptoms = models.TextField(blank=True)

    class Meta:
        db_table = 'core_appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.date} {self.time})"

    @property
    def is_upcoming(self):
        """Проверяет, является ли запись будущей"""
        appointment_datetime = timezone.datetime.combine(self.date, self.time)
        return appointment_datetime > timezone.now()


class DoctorReview(BaseModel):
    """Отзывы о врачах"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reviews_given')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='review', null=True, blank=True)

    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    # Новые поля
    would_recommend = models.BooleanField(default=True)
    wait_time_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)

    class Meta:
        db_table = 'core_doctor_reviews'
        verbose_name = 'Doctor Review'
        verbose_name_plural = 'Doctor Reviews'
        unique_together = ['doctor', 'patient', 'appointment']

    def __str__(self):
        return f"Review for Dr. {self.doctor.user.full_name} by {self.patient}"


class MedicalRecord(BaseModel):
    """Медицинская карта пациента (история приёмов и лечения)"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    files = models.FileField(upload_to='medical_records/', blank=True, null=True)

    class Meta:
        db_table = 'core_medical_records'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-created_at']

    def __str__(self):
        return f"Record for {self.patient} ({self.created_at.strftime('%Y-%m-%d')})"


class Prescription(BaseModel):
    """Рецепты и назначения врача"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)

    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.medication_name} для {self.patient}"


class Payment(BaseModel):
    """Платежи за услуги"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ],
        default='pending'
    )
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'core_payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.amount} - {self.patient}"


class Notification(BaseModel):
    """Уведомления для пользователей"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('appointment_reminder', 'Appointment Reminder'),
            ('appointment_confirmation', 'Appointment Confirmation'),
            ('prescription_ready', 'Prescription Ready'),
            ('general', 'General')
        ],
        default='general'
    )
    is_read = models.BooleanField(default=False)
    related_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'core_notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"