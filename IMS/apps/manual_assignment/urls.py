from django.urls import path
from . import views

app_name = 'manual_assignment'

urlpatterns = [
    path('', views.manual_assignment, name='manual_assignment'),
    path('assign/', views.assign_staff_to_slot, name='assign_staff_to_slot'),
    path('unassign/', views.unassign_staff_from_slot, name='unassign_staff_from_slot'),
    path('get-available-staff/', views.get_available_staff, name='get_available_staff'),
    path('get-staff-assignments/', views.get_staff_assignments, name='get_staff_assignments'),
    path('manual-assignment/get-eligible-staff/', views.get_eligible_staff, name='get-eligible-staff'),
    path('get-all-staff-assignments/', views.get_all_staff_assignments, name='get_all_staff_assignments'),

]
