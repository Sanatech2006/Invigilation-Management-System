from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import ExamDate
from django.utils.dateparse import parse_date
def exam_dates_view(request):
    return render(request, 'exam_dates/exam_dates.html') 

@csrf_exempt  # Only if you're not sending CSRF token correctly; better to handle CSRF properly with tokens
def save_exam_date(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
    
    try:
        data = json.loads(request.body)
        date_str = data.get("date")
        if not date_str:
            return JsonResponse({"success": False, "error": "Date not provided"})
        
        date_obj = parse_date(date_str)
        if not date_obj:
            return JsonResponse({"success": False, "error": "Invalid date format"})
        
        # Create or skip duplicate
        obj, created = ExamDate.objects.get_or_create(date=date_obj)
        
        if created:
            return JsonResponse({"success": True, "message": "Date saved successfully"})
        else:
            return JsonResponse({"success": False, "error": "Date already exists"})
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})