from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.dateparse import parse_date
import json
from .models import ExamDate


def exam_dates_view(request):
    return render(request, 'exam_dates/exam_dates.html')


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


@require_GET
def get_exam_dates(request):
    try:
        data = [
            {
                "day_no": ed.day_no,
                "date": ed.date.strftime("%Y-%m-%d")
            }
            for ed in ExamDate.objects.order_by("date")
        ]
        return JsonResponse({"success": True, "exam_dates": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
