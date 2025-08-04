# IMS/apps/invigilation_schedule/apps.py
from django.apps import AppConfig

class InvigilationScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.invigilation_schedule'
    label = 'invigilation_schedule'  # Add this line