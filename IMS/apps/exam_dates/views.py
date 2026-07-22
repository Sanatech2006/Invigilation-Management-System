from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils.dateparse import parse_date
import json
from .models import ExamDate

from apps.settings.models import GlobalSettings

def exam_dates_view(request):
    # Always read fresh from DB — never use a cached row
    gs = GlobalSettings.objects.filter(id=1).first()
    display_reports = gs.display_reports_to_staff if gs else False

    response = render(request, 'exam_dates/exam_dates.html', {
        'display_reports': display_reports
    })
    # Prevent the browser from caching this page so the toggle state
    # is always loaded fresh from the database on every visit.
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@require_POST
def save_exam_date(request):
    data = json.loads(request.body)

    date_str = data.get("date")
    day_no = data.get("day_number")  # frontend name

    date_obj = parse_date(date_str)

    if not date_obj or not day_no:
        return JsonResponse({"success": False, "error": "Invalid input"})

    if ExamDate.objects.filter(date=date_obj).exists():
        return JsonResponse({"success": False, "error": "This date already exists."})

    if ExamDate.objects.filter(day_no=day_no).exists():
        return JsonResponse({"success": False, "error": "This day sequence already exists."})

    obj = ExamDate.objects.create(
        date=date_obj,
        day_no=day_no
    )

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
            return JsonResponse({"success": False, "error": "This date already exists."})
            
        if ExamDate.objects.filter(day_no=day_no).exclude(pk=pk).exists():
            return JsonResponse({"success": False, "error": "This day sequence already exists."})

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
