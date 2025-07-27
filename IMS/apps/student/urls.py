from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_upload_view.as_view(), name='student_upload'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='delete_student'),
]
