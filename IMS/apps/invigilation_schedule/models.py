from django.db import models

class InvigilationSchedule(models.Model):
    serial_number = models.AutoField(primary_key=True)
    date = models.DateField()
    session = models.CharField(max_length=20, blank=True, null=True)
    hall_no = models.CharField(max_length=50)
    hall_department = models.CharField(max_length=100)
    hall_dept_category = models.CharField(max_length=100,null=True)
    staff_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    staff_category = models.CharField(max_length=100, blank=True, null=True)
    dept_category=models.CharField(max_length=100,null=True)
    double_session = models.BooleanField(default=False)
    dept_name=models.CharField(max_length=100,null=True)
    
    class Meta:
        db_table = 'invigilation_schedule'
    
    def __str__(self):
        return f"{self.date} - {self.hall_no}"