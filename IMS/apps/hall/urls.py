from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.hall_management, name='hall_management'),
    path('upload/', views.upload_rooms, name='upload_rooms'),
    path('download-template/', views.download_template, name='download_template'),
]