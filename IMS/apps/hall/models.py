from django.db import models

class Room(models.Model):
    dept_category = models.CharField(max_length=100)
    block = models.CharField(max_length=100, default="-")
    dept_name = models.CharField(max_length=100)
    hall_no = models.CharField(max_length=50, unique=True)
    strength = models.PositiveIntegerField(default=0)
    benches = models.PositiveIntegerField(default=0)
    days = models.IntegerField(default=0)  # Fixed: removed max_length
    staff_allotted = models.CharField(max_length=20, default="Not Allotted")
    staff_required = models.IntegerField(default=1)  # or whatever field type you're using
    required_session = models.IntegerField(default=2)
    
    # export Room='Room'