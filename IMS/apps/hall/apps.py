from django.apps import AppConfig

class HallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hall'  # Note the name matches the directory
    verbose_name = 'Hall Management'
