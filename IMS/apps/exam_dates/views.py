from django.shortcuts import render

def exam_dates_view(request):
    return render(request, 'exam_dates/exam_dates.html') 
