from django.db import models

class Student(models.Model):
    batch = models.CharField(max_length=10)
    dept_id = models.CharField(max_length=10)
    degree = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    reg_no = models.CharField(max_length=20, unique=True)
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    category = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.reg_no})"
