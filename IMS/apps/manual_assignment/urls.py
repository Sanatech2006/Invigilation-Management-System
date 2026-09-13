from django.urls import path
from . import views

app_name = 'manual_assignment'

urlpatterns = [
    path('', views.manual_assignment, name='manual_assignment'),
    path('assign-staff/', views.manual_assignment, name='assign_staff'),
    path('assign/', views.assign_staff_to_slot, name='assign_staff_to_slot'),
    path('unassign/', views.unassign_staff_from_slot, name='unassign_staff_from_slot'),
    path('get-available-staff/', views.get_available_staff, name='get_available_staff'),
    path('get-staff-assignments/', views.get_staff_assignments, name='get_staff_assignments'),
    path('manual-assignment/get-eligible-staff/', views.get_eligible_staff, name='get-eligible-staff'),
    path('get-all-staff-assignments/', views.get_all_staff_assignments, name='get_all_staff_assignments'),
    path('auto-assign/', views.auto_assign_staff, name='auto_assign_staff'),
    
    # Staff Swap Workflow Endpoints
    path('staff-swap/', views.staff_swap, name='staff_swap'),
    path('staff-swap/get-unassigned-halls/', views.get_swap_unassigned_halls, name='get_swap_unassigned_halls'),
    path('staff-swap/get-available-dates/', views.get_swap_available_dates, name='get_swap_available_dates'),
    path('staff-swap/find-eligible-staff/', views.find_eligible_swap_staff, name='find_eligible_swap_staff'),
    path('staff-swap/perform-swap/', views.perform_staff_swap, name='perform_staff_swap'),
]

