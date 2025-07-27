from django.apps import AppConfig

class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.staff'  # Must match the Python path
    label = 'staff'  # The short name you'll reference
    verbose_name = 'Staff Management'