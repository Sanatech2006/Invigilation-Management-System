from django.shortcuts import render
from django.views import View

def hall_management(request):
    return render(request, 'hall/hall_management.html')