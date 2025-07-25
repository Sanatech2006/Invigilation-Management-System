from django.db import models

class Room(models.Model):
    DeptType = models.CharField(max_length=100)
    Block = models.CharField(max_length=100)
    DeptName = models.CharField(max_length=100)
    HallNo = models.CharField(max_length=50, unique=True)
    Strength = models.PositiveIntegerField()
    Benches = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.HallNo} - {self.Block}"
