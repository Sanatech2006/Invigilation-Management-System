from django.urls import path
from . import views
from .views import generate_schedule
from .views import export_schedule_excel
from .views import assign_staff
from .views import generate_session
from .views import swap_slots 

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
    path('swap_slots/', swap_slots, name='swap_slots'),
    path('api/list_hall_numbers/', views.list_hall_numbers, name='list_hall_numbers'),
    path('api/get_hall_details/', views.get_hall_details, name='get_hall_details'),
    path('api/delete/', views.delete_hall, name='delete_hall'),
    path('api/update-hall/', views.update_hall, name='update_hall'),
    path('api/add-hall/', views.add_hall, name='add_hall'),

] 
