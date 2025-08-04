# exam_date/models.py
from django.db import models

class ExamDate(models.Model):
    day_no = models.AutoField(primary_key=True)
    date = models.DateField(unique=True)
    
    class Meta:
        db_table = 'exam_date'  
        verbose_name = "Exam Date"
        verbose_name_plural = "Exam Dates"
    
    def __str__(self):
        return f"Day {self.day_no} - {self.date}"