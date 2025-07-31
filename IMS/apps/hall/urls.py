from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.hall_management, name='hall_management'),  # Changed to hall_management
    path('management/upload/', views.hall_management, name='hall_upload'),
    path('list/', views.hall_list, name='hall_list'),
] 