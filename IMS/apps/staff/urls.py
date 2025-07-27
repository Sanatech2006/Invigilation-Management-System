from django.urls import path
from .views import staff_management

app_name = 'staff'  
urlpatterns = [
    path('management/', staff_management, name='staff-management'),  
]