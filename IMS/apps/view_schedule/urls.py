from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_schedule, name='view_schedule'),
]