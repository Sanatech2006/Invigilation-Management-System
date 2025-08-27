from django.db import models

class InvigilationConstraint(models.Model):
    # If you have a different primary key field (e.g., 'name')
    name = models.CharField(max_length=100, primary_key=True)
    
    # Or if you need to add an id field:
    # id = models.AutoField(primary_key=True)
    
    enabled = models.BooleanField(default=True)
    is_hard = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'new_constraints'  # Explicitly set the table name
    
    def __str__(self):
        return self.name
