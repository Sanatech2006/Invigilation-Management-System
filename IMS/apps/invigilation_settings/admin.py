from django.contrib import admin
from .models import InvigilationConstraint

@admin.register(InvigilationConstraint)
class InvigilationConstraintAdmin(admin.ModelAdmin):
    list_display = [
        'name',          # primary key field
        'enabled',       # Boolean field
        'is_hard',       # Boolean field
        'locked'         # Boolean field
    ]
    
    list_editable = [
        'enabled',
        'is_hard',
        'locked'
    ]
    
    search_fields = ['name']
    list_filter = ['enabled', 'is_hard', 'locked']
    