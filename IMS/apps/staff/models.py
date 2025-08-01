from django.db import models
from django.core.validators import validate_email, RegexValidator

class Department(models.Model):
    app_label = 'staff'
    """Department model to store department types and names"""
    DEPT_TYPE_CHOICES = [
        ('AIDED', 'Aided'),
        ('SFM', 'sfm'),
        ('SFW', 'sfw'),
    ]
    
    dept_type = models.CharField(max_length=20, choices=DEPT_TYPE_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name 

class Designation(models.Model):
    app_label = 'staff'
    """Designation model"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50) 
    
    def __str__(self):
        return self.name 

class Staff(models.Model):
    app_label = 'staff'
    """Main staff model"""
    dept_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Department Name (from Excel)",
        help_text="Original department name from Excel import"
    )
    
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    
    # New fields replacing department FK and category
    staff_category = models.CharField(max_length=100)
    dept_category = models.CharField(max_length=100)
    
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )
    mobile = models.CharField(validators=[phone_regex], max_length=20, blank=True)
    email = models.EmailField(validators=[validate_email], blank=True)
    
    date_of_joining = models.TextField(null=True, blank=True)  # This would cause your issue
    
    is_active = models.BooleanField(default=True)
    session = models.IntegerField(  # Changed from PositiveIntegerField
        default=0,
        help_text="Dynamically allocated session value (can be negative)"
    )
    fixed_session = models.IntegerField(  # Changed from PositiveIntegerField
        default=0,
        help_text="Fixed session allocation (can be negative)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'staff'
        verbose_name_plural = "Staff"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.staff_id} - {self.name} ({self.designation})"