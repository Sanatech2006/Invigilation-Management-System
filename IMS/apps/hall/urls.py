from django.urls import path
from . import views
from .views import generate_schedule
from .views import export_schedule_excel
from .views import assign_staff
from .views import generate_session

urlpatterns = [
    path('management/', views.hall_management, name='hall_management'),  # Changed to hall_management
    path('management/upload/', views.hall_management, name='hall_upload'),
    path('list/', views.hall_list, name='hall_list'),
     path('generate-schedule/', generate_schedule, name='generate_schedule'),
    path('export-staff-excel/', export_schedule_excel, name='export_schedule_excel'),
    path('assign-staff/', views.assign_staff, name='assign_staff'),
    path('generate_session/', generate_session, name='generate_session'),
    path('download-room-data/', views.download_room_data, name='download_room_data'),
    path("download-staff-unallotted/", views.download_staff_unallotted, name="download_staff_unallotted"),

] 
