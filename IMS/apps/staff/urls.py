from django.urls import path
from .views import staff_management
from . import views


app_name = 'staff'  
urlpatterns = [
    path('management/', views.staff_management, name='staff-management'),
     path("download/", views.download_staff_data, name="download_staff_data"),
    
]