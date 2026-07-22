from django.urls import path
from . import views

app_name = 'exam_dates'

urlpatterns = [
    path('', views.exam_dates_view, name='index'),
    path('save/', views.save_exam_date, name='save'),
    path('list/', views.get_exam_dates, name='list'),
    path('update/<int:pk>/', views.update_exam_date, name='update'),
    path('delete/<int:pk>/', views.delete_exam_date, name='delete'),
]