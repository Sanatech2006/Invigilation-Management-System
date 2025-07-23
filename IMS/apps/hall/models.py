# from django.db import models
# from apps.staff.models import Department

# class Hall(models.Model):
#     name = models.CharField(max_length=50)
#     code = models.CharField(max_length=10, unique=True)
#     capacity = models.PositiveIntegerField()
#     departments = models.ManyToManyField(Department)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.name} ({self.code}) - Cap: {self.capacity}"