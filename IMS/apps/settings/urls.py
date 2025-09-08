from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_home, name='settings_home'),
    path('change-password/', views.change_password_no_auth, name='change_password'),
]

