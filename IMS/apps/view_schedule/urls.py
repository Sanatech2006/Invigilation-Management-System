from django.urls import path
from .views import view_schedule
from .views import download_schedule_excel
from . import views

urlpatterns = [
    path('view-schedule/', view_schedule, name='view_schedule'),
    path('filter/', views.filter_schedule, name='filter_schedule'),
    path('download-excel/', download_schedule_excel, name='download_schedule_excel'),
]