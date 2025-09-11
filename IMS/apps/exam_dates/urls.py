# apps/exam_dates/urls.py

from django.urls import path
from . import views

app_name = 'exam_dates'  # ✅ Important if you're using a namespace

urlpatterns = [
    path('', views.exam_dates_view, name='index'),  # or any name you prefer
    path('save/', views.save_exam_date, name='exam_dates_save'),
    path('list/', views.get_exam_dates, name='get_exam_dates'),

]
