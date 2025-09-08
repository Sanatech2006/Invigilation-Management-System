from django.urls import path
from . import views

  # optional but recommended namespace

urlpatterns = [
    path('reports/', views.reports_view, name='reports'),
    path('hod/', views.hod_view, name='hod_reports'),  
    path('admin/', views.admin_view, name='admin_reports'),
    # Add other report-specific paths here
]
