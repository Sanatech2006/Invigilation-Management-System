from django.contrib import admin
from .models import Staff  

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'dept_category','staff_category', 'designation', 'mobile', 'is_active')  
