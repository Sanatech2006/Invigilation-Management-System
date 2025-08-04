from django.shortcuts import render

def view_schedule(request):
    return render(request, 'view_schedule/view_schedule.html')