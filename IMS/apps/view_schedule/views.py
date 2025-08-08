# IMS/apps/view_schedule/views.py
from django.shortcuts import render
from apps.invigilation_schedule.models import InvigilationSchedule
import openpyxl
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q


def view_schedule(request):
    print("\n===== VIEW SCHEDULE REQUEST =====")  # Debug
    print(f"Request method: {request.method}")  # Debug
    
    # Initialize context with all required data
    context = {
    'schedules': InvigilationSchedule.objects.all(),
    'dates': InvigilationSchedule.objects.dates('date', 'day').distinct(),
    'sessions': InvigilationSchedule.objects.values_list('session', flat=True).distinct(),
    'hall_numbers': InvigilationSchedule.objects.values_list('hall_no', flat=True).distinct(),
    'staff_names': InvigilationSchedule.objects.exclude(name__isnull=True)
                                               .exclude(name__exact='')
                                               .values_list('name', flat=True)
                                               .distinct(),

    # Additional fields
    'hall_dept_categories': InvigilationSchedule.objects.values_list('hall_dept_category', flat=True).distinct(),
    'designations': InvigilationSchedule.objects.values_list('designation', flat=True).distinct(),
    'staff_categories': InvigilationSchedule.objects.values_list('staff_category', flat=True).distinct(),
    'dept_categories': InvigilationSchedule.objects.values_list('dept_category', flat=True).distinct(),
    'double_sessions': InvigilationSchedule.objects.values_list('double_session', flat=True).distinct(),
}

    
    # Debug output
    print(f"Found {len(context['schedules'])} schedules")  # Debug
    print(f"Found {len(context['staff_names'])} staff names")  # Debug
    # Temporary debug - add right before return
    print("All schedules from DB:")
    for s in context['schedules']:
     print(f"{s.serial_number} | {s.date} | {s.name}")
    
    return render(request, 'view_schedule/view_schedule.html', context)


def download_schedule_excel(request):
    # Create a workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # Define headers
    headers = [
        'S.No', 'Date', 'Session', 'Hall No', 'Hall Department',
        'Staff ID', 'Name', 'Designation', 'Staff Category',
        'Department Category', 'Double Session'
    ]
    ws.append(headers)

    # Get all data
    schedules = InvigilationSchedule.objects.all()
    for schedule in schedules:
        ws.append([
            schedule.serial_number,
            schedule.date.strftime("%Y-%m-%d") if schedule.date else '',
            schedule.session or '-',
            schedule.hall_no,
            schedule.hall_department,
            schedule.staff_id or '-',
            schedule.name or '-',
            schedule.designation or '-',
            schedule.staff_category or '-',
            schedule.dept_category or '-',
            "Yes" if schedule.double_session else "No"
        ])

    # Create HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=invigilation_schedule.xlsx'
    wb.save(response)
    return response


def filter_schedule(request):
    date = request.GET.get('date')
    hall_department = request.GET.get('hall_department')
    staff_id = request.GET.get('staff_id')
    dept_category = request.GET.get('dept_category')

    filters = Q()
    if date:
        filters &= Q(date=date)
    if hall_department:
        filters &= Q(hall_department=hall_department)
    if staff_id:
        filters &= Q(staff_id=staff_id)
    if dept_category:
        filters &= Q(dept_category=dept_category)

    schedules = InvigilationSchedule.objects.filter(filters)

    data = []
    for s in schedules:
        data.append({
            'serial_number': s.serial_number,
            'date': s.date.strftime("%Y-%m-%d") if s.date else '',
            'session': s.session,
            'hall_no': s.hall_no,
            'hall_department': s.hall_department,
            'staff_id': s.staff_id,
            'name': s.name,
            'designation': s.designation,
            'staff_category': s.staff_category,
            'dept_category': s.dept_category,
            'double_session': "Yes" if s.double_session else "No"
        })

    return JsonResponse({'schedules': data})