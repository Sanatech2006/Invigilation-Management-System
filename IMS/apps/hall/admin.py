from django.contrib import admin
from .models import Room  

@admin.register(Room)
class HallAdmin(admin.ModelAdmin):
    list_display = ('dept_category', 'dept_name', 'hall_no', 'strength', 'days' ) 
