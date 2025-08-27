from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('SCHEDULER', 'Scheduler'),
        ('VIEWER', 'Viewer'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='VIEWER')
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
