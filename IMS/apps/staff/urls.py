from django.urls import path
from .views import staff_management

urlpatterns = [
     path('staff/', staff_management, name='staff-management'),
]