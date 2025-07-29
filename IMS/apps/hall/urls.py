from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.hall_management, name='hall_management'),
]