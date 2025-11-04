import django_filters
from .models import Doctor, Appointment


class DoctorFilter(django_filters.FilterSet):
    min_experience = django_filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    max_experience = django_filters.NumberFilter(field_name='experience_years', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='consultation_fee', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='consultation_fee', lookup_expr='lte')

    class Meta:
        model = Doctor
        fields = ['specialization', 'is_available', 'is_verified']