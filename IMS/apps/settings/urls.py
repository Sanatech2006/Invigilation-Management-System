from django.urls import path
from . import views
from .views import upload_schedule

app_name = 'settings'

urlpatterns = [
    path('', views.settings_home, name='settings_home'),
    path('change-password/', views.change_password_no_auth, name='change_password'),
    path('upload-schedule/', upload_schedule, name='upload_schedule'),
]

