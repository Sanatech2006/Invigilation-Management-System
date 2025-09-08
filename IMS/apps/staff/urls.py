from django.urls import path
from .views import staff_management
from . import views


app_name = 'staff'  
urlpatterns = [
    path('management/', views.staff_management, name='staff-management'),
    path("download/", views.download_staff_data, name="download_staff_data"),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('api/get-staff-details/', views.get_staff_details, name='get_staff_details'),
    path('api/search-staff/', views.search_staff, name='search_staff'),
    path('api/test/', views.test_api, name='test_api'),
    path('api/update-staff/', views.update_staff, name='update_staff'),
    path('api/delete-staff/', views.delete_staff, name='delete_staff'),
]
