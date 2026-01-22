from django.urls import path
from . import views

app_name = 'exam_dates'

urlpatterns = [
    path('', views.exam_dates_view, name='index'),
    path('save/', views.save_exam_date, name='save'),
    path('list/', views.get_exam_dates, name='list'),
]