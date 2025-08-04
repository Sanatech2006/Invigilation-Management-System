from django.urls import path
from . import views

urlpatterns = [
    path('invigilation_settings/', views.invigilation_settings, name='invigilation_settings'),
     path('update_constraints/', views.update_constraints, name='update_constraints'),
]