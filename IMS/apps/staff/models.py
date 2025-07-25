from django.db import models
from django.core.validators import validate_email, RegexValidator

class Department(models.Model):
    """Department model to store department types and names"""
    DEPT_TYPE_CHOICES = [
        ('ACADEMIC', 'Academic'),
        ('ADMIN', 'Administrative'),
        ('SUPPORT', 'Support Staff'),
    ]
    
    dept_type = models.CharField(max_length=20, choices=DEPT_TYPE_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.get_dept_type_display()} - {self.name}"

class Designation(models.Model):
    """Designation model"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # Teaching/Non-Teaching etc.
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class Staff(models.Model):
    """Main staff model"""
    CATEGORY_CHOICES = [
        ('TEACHING', 'Teaching'),
        ('NON_TEACHING', 'Non-Teaching'),
        ('CONTRACT', 'Contract'),
        ('VISITING', 'Visiting Faculty'),
    ]
    
    # Core fields
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(validators=[validate_email], blank=True)
    
    # Dates
    date_of_joining = models.DateField(null=True, blank=True)
    
    # System fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Staff"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.staff_id} - {self.name} ({self.designation})"