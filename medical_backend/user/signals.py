from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from core.models import UserProfile, DoctorProfile, ClientProfile, ManagerProfile  # если профили в core

@receiver(post_save, sender=CustomUser)
def create_user_profiles(sender, instance, created, **kwargs):
    """Автоматически создаем профили при создании пользователя"""
    if created:
        # Создаем базовый профиль для всех пользователей
        UserProfile.objects.get_or_create(user=instance)

        # Создаем специфические профили в зависимости от роли
        if instance.role == 'doctor':
            DoctorProfile.objects.get_or_create(user=instance)
        elif instance.role == 'client':
            ClientProfile.objects.get_or_create(user=instance)
        elif instance.role == 'manager':
            ManagerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profiles(sender, instance, **kwargs):
    """Сохраняем связанные профили"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    if instance.role == 'doctor' and hasattr(instance, 'doctorprofile'):
        instance.doctorprofile.save()
    elif instance.role == 'client' and hasattr(instance, 'clientprofile'):
        instance.clientprofile.save()
    elif instance.role == 'manager' and hasattr(instance, 'managerprofile'):
        instance.managerprofile.save()