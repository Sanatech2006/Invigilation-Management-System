from django.urls import path
from . import views
from .views import generate_schedule
from .views import export_schedule_excel

urlpatterns = [
    path('management/', views.hall_management, name='hall_management'),  # Changed to hall_management
    path('management/upload/', views.hall_management, name='hall_upload'),
    path('list/', views.hall_list, name='hall_list'),
     path('generate-schedule/', generate_schedule, name='generate_schedule'),
    path('export-staff-excel/', export_schedule_excel, name='export_schedule_excel'),
] 