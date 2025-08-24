from django.urls import path
from .views import generate_schedule, view_schedule
from . import views
from .views import schedule_api, view_schedule
from .views import session_staff_delete


urlpatterns = [
    path('api/schedule/', schedule_api, name='schedule_api'),
    path('view/', view_schedule, name='view_schedule'),
    path("api/filter-options/", views.get_filter_options, name="get_filter_options"),
    path("api/filtered-schedule/", views.get_filtered_schedule, name="get_filtered_schedule"),
    path('get_available_staff/', views.get_available_staff, name='get_available_staff'),
]