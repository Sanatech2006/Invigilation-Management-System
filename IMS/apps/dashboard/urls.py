from django.urls import path
from .views import DashboardView, StaffAvailabilityView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('staff-availability/', StaffAvailabilityView.as_view(), name='staff_availability'),
    path('check-staff-availability/', StaffAvailabilityView.as_view(), name='check_staff_availability'),
]

