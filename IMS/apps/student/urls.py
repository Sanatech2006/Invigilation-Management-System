from django.urls import path
from .views import student_upload_view

urlpatterns = [
    path('upload/', student_upload_view.as_view(), name='student_upload'),
]