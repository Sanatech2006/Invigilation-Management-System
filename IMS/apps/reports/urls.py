# reports/urls.py
app_name = 'reports'
from django.urls import path
from . import views

urlpatterns = [
    path('own-schedule/', views.own_schedule, name='own_schedule'),
    path('visiting-staff/', views.visiting_staff, name='visiting_staff'),
    path('department-staff-out/', views.department_staff_out, name='department_staff_out'),
    path('squad-schedule/', views.squad_schedule, name='squad_schedule'),
    path('schedule-report/', views.schedule_report, name='schedule_report'),
    path('squad-report/', views.squad_report, name='squad_report'),
]
