# core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Management'

    def ready(self):
        # import core.signals  # 👈 ЗАКОММЕНТИРУЙ ЭТУ СТРОКУ
        pass