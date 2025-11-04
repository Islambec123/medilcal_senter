# accounts/custom_admin.py
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class MedicalAdminSite(AdminSite):
    site_header = "Medical Portal Administration"
    site_title = "Medical Portal Admin"
    index_title = "Welcome to Medical Portal Administration"

    def get_app_list(self, request):
        """
        Кастомизация порядка приложений в админке
        """
        app_list = super().get_app_list(request)
        # Переупорядочиваем приложения по важности
        reordered_app_list = []
        accounts_app = None

        for app in app_list:
            if app['app_label'] == 'accounts':
                accounts_app = app
            else:
                reordered_app_list.append(app)

        if accounts_app:
            reordered_app_list.insert(0, accounts_app)

        return reordered_app_list


medical_admin_site = MedicalAdminSite(name='medical_admin')

from .models import User, UserProfile, DoctorProfile, ClientProfile, ManagerProfile, DoctorSpecialization
from .admin import (
    CustomUserAdmin, UserProfileAdmin, DoctorProfileAdmin,
    ClientProfileAdmin, ManagerProfileAdmin, DoctorSpecializationAdmin
)

medical_admin_site.register(User, CustomUserAdmin)
medical_admin_site.register(UserProfile, UserProfileAdmin)
medical_admin_site.register(DoctorProfile, DoctorProfileAdmin)
medical_admin_site.register(ClientProfile, ClientProfileAdmin)
medical_admin_site.register(ManagerProfile, ManagerProfileAdmin)
medical_admin_site.register(DoctorSpecialization, DoctorSpecializationAdmin)