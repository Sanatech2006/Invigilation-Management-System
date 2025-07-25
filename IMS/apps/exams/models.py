from django.db import models

class ExamSession(models.Model):
    SHIFT_CHOICES = [
        ('FN', 'Forenoon'),
        ('AN', 'Afternoon'),
    ]

    SESSION_CHOICES = [
        (1, 'Session 1'),
        (2, 'Session 2'),
    ]

    STUDENT_TYPE_CHOICES = [
        ('SFM', 'SFM Students'),
        ('SFW', 'SFW Students'),
    ]

    exam_date = models.DateField()
    shift = models.CharField(max_length=2, choices=SHIFT_CHOICES)
    session_number = models.IntegerField(choices=SESSION_CHOICES)
    student_type = models.CharField(max_length=3, choices=STUDENT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.exam_date} - {self.shift} - Session {self.session_number} ({self.student_type})"
