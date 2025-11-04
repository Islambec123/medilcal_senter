from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, UserProfile, DoctorProfile


class AdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            full_name='Admin User'
        )
        self.client.force_login(self.superuser)

    def test_admin_access(self):
        """Тест доступа к кастомной админке"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Portal Administration')

    def test_user_admin_display(self):
        """Тест отображения пользователей в админке"""
        response = self.client.get('/admin/user/user/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile_links')

    def test_doctor_profile_creation(self):
        """Тест автоматического создания профиля доктора"""
        doctor = User.objects.create_user(
            email='doctor@example.com',
            password='doctorpass123',
            role='doctor',
            full_name='Dr. Smith'
        )

        # Проверяем, что профили создались автоматически
        self.assertTrue(hasattr(doctor, 'profile'))
        self.assertTrue(hasattr(doctor, 'doctorprofile'))

        # Проверяем доступ в админке
        response = self.client.get(f'/admin/user/user/{doctor.id}/change/')
        self.assertEqual(response.status_code, 200)


class SignalTests(TestCase):
    def test_profile_creation_signals(self):
        """Тест сигналов создания профилей"""
        # Создаем пользователей разных ролей
        client = User.objects.create_user(
            email='client@example.com',
            password='clientpass123',
            role='client'
        )
        doctor = User.objects.create_user(
            email='doctor2@example.com',
            password='doctorpass123',
            role='doctor'
        )
        manager = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            role='manager'
        )

        # Проверяем, что создались правильные профили
        self.assertTrue(hasattr(client, 'profile'))
        self.assertTrue(hasattr(client, 'clientprofile'))
        self.assertFalse(hasattr(client, 'doctorprofile'))

        self.assertTrue(hasattr(doctor, 'profile'))
        self.assertTrue(hasattr(doctor, 'doctorprofile'))

        self.assertTrue(hasattr(manager, 'profile'))
        self.assertTrue(hasattr(manager, 'managerprofile'))