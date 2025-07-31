# apps/exam_dates/urls.py

from django.urls import path
from . import views

app_name = 'exam_dates'  # ✅ Important if you're using a namespace

urlpatterns = [
    path('', views.exam_dates_view, name='index'),  # or any name you prefer
]
