from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils.dateparse import parse_date
import json
from .models import ExamDate

from apps.settings.models import GlobalSettings

def exam_dates_view(request):
    settings = GlobalSettings.get_settings()
    return render(request, 'exam_dates/exam_dates.html', {
        'display_reports': settings.display_reports_to_staff
    })


@require_POST
def save_exam_date(request):
    data = json.loads(request.body)

    date_str = data.get("date")
    day_no = data.get("day_number")  # frontend name

    date_obj = parse_date(date_str)

    if not date_obj or not day_no:
        return JsonResponse({"success": False, "error": "Invalid input"})

    obj, created = ExamDate.objects.get_or_create(
        date=date_obj,
        defaults={"day_no": day_no}
    )

    if not created:
        return JsonResponse({"success": False, "error": "Date already exists"})

    return JsonResponse({
        "success": True,
        "date": obj.date.strftime("%Y-%m-%d"),
        "day_no": obj.day_no
    })


@require_POST
def update_exam_date(request, pk):
    try:
        data = json.loads(request.body)
        date_str = data.get("date")
        day_no = data.get("day_number")

        date_obj = parse_date(date_str)
        if not date_obj or not day_no:
            return JsonResponse({"success": False, "error": "Invalid input"})

        if ExamDate.objects.filter(date=date_obj).exclude(pk=pk).exists():
            return JsonResponse({"success": False, "error": "Date already exists"})
            
        if ExamDate.objects.filter(day_no=day_no).exclude(pk=pk).exists():
            return JsonResponse({"success": False, "error": "Day sequence already exists"})

        ExamDate.objects.filter(pk=pk).update(date=date_obj, day_no=day_no)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["DELETE"])
def delete_exam_date(request, pk):
    try:
        ExamDate.objects.filter(pk=pk).delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def get_exam_dates(request):
    try:
        data = [
            {
                "id": ed.day_no,
                "day_no": ed.day_no,
                "date": ed.date.strftime("%Y-%m-%d")
            }
            for ed in ExamDate.objects.order_by("date")
        ]
        return JsonResponse({"success": True, "exam_dates": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
