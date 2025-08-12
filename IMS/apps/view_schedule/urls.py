from django.urls import path
from .views import view_schedule
from .views import download_schedule_excel
from . import views
from .views import session_staff_delete
from .views import staff_edit_session, get_available_staff


urlpatterns = [
    path('view-schedule/', view_schedule, name='view_schedule'),
    path('filter/', views.filter_schedule, name='filter_schedule'),
    path('download-excel/', download_schedule_excel, name='download_schedule_excel'),
    path('staff_delete_session/', session_staff_delete, name='staff_delete_session'),
    path('staff_edit_session/', staff_edit_session, name='staff_edit_session'),
    path('get-available-staff/', get_available_staff, name='get_available_staff'),

]