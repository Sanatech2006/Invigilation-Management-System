# from django.db import models

# class Department(models.Model):
#     name = models.CharField(max_length=100)
#     code = models.CharField(max_length=10, unique=True)

#     def __str__(self):
#         return f"{self.name} ({self.code})"

# class Staff(models.Model):
#     CATEGORIES = (
#         ('TEACHING', 'Teaching'),
#         ('NON_TEACHING', 'Non-Teaching'),
#     )
    
#     user = models.OneToOneField('core.User', on_delete=models.CASCADE)
#     staff_id = models.CharField(max_length=20, unique=True)
#     department = models.ForeignKey(Department, on_delete=models.PROTECT)
#     category = models.CharField(max_length=20, choices=CATEGORIES)
#     designation = models.CharField(max_length=100)
#     is_available = models.BooleanField(default=True)
    
#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.designation}"