# IMS/apps/view_schedule/views.py
from django.shortcuts import render,redirect
from django.db.models.functions import Lower, Trim
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.forms.models import model_to_dict
from apps.invigilation_schedule.models import InvigilationSchedule
import openpyxl
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from ..hall.models import Room
from ..invigilation_schedule.models import InvigilationSchedule
from datetime import datetime
from ..staff.models import Staff
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery, IntegerField, Count, F
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET
from django.db.models.functions import Cast

def view_schedule(request):
    print("\n===== VIEW SCHEDULE REQUEST =====")  # Debug
    print(f"Request method: {request.method}")  # Debug
    
    # Initialize context with all required data
    context = {
    'schedules': InvigilationSchedule.objects.all().order_by(
        'dept_category', 'date',  'hall_department', 'hall_no'
    ),
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
    
    return render(request, 'view_schedule/view_schedule.html', context)


def download_schedule_excel(request):
    # Create a workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # Define headers
    headers = [
        'S.No', 'Date', 'Session', 'Hall No', 'Hall Department',
        'Staff Department', 'Staff ID', 'Name', 'Designation', 'Staff Category',
        'Department Category', 'Hall Dept Category', 'Double Session',
    ]
    ws.append(headers)

    # Get all data
    schedules = InvigilationSchedule.objects.all()
    for schedule in schedules:
        row = [
            schedule.serial_number,
            schedule.date.strftime("%Y-%m-%d") if schedule.date else '',
            schedule.session or '-',
            schedule.hall_no,
            schedule.hall_department,
            schedule.dept_name,
            schedule.staff_id or '-',
            schedule.name or '-',
            schedule.designation or '-',
            schedule.staff_category or '-',
            schedule.dept_category or '-',
            schedule.hall_dept_category or '-',
            "Yes" if schedule.double_session else "No",
        ]
        print(row)  # Debugging line
        ws.append(row)
    
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
            'dept_name': s.dept_name,  
            'staff_id': s.staff_id,
            'name': s.name,
            'designation': s.designation,
            'staff_category': s.staff_category,
            'dept_category': s.dept_category,
            'double_session': "Yes" if s.double_session else "No",
             
        })

    return JsonResponse({'schedules': data})

from django.shortcuts import redirect
from datetime import datetime
from apps.invigilation_schedule.models import InvigilationSchedule


# def get_available_staff(request):
#     try:
#         # 1) Params from client (row staff dept_category must be passed here)
#         date = request.GET.get('date')
#         session = request.GET.get('session')
#         target_category = request.GET.get('hall_category')  # this should carry the row's staff dept_category

#         print('get_available_staff params:', date, session, target_category)

#         # 2) Validate and normalize
#         missing = [k for k, v in {'date': date, 'session': session, 'hall_category': target_category}.items() if not v]
#         if missing:
#             return JsonResponse({"error": f"Missing params: {', '.join(missing)}"}, status=400)

#         norm_cat = (target_category or '').strip().lower()

#         # 3) Busy staff at this exact date+session (exclude those already assigned)
#         busy_ids = list(
#             InvigilationSchedule.objects
#             .filter(date=date, session=session)
#             .exclude(staff_id__isnull=True)
#             .values_list('staff_id', flat=True)
#         )
#         print('busy_ids count:', len(busy_ids))

#         # 4) Strict same-category filter with normalization, and exclude busy staff
#         staff_qs = (
#             Staff.objects
#             .annotate(dc_norm=Lower(Trim('dept_category')))
#             .filter(is_active=True, dc_norm=norm_cat)
#             .exclude(staff_id__in=busy_ids)
#             .order_by('staff_id')
#         )

#         # Sanity: ensure we only have the target category
#         cats = list(staff_qs.values_list('dept_category', flat=True).distinct())
#         print('target category (normalized):', norm_cat, 'distinct categories in result:', cats)

#         # 5) Return only id, name, and category for verification
#         staff_list = list(staff_qs.values('staff_id', 'name', 'dept_category'))

#         return JsonResponse({"staff": staff_list})

#     except Exception as e:
#         print("Error in get_available_staff:", str(e))
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": "Internal server error"}, status=500)


@require_GET
def get_available_staff(request):
    try:
        date = request.GET.get('date')
        session = request.GET.get('session')
        row_dept_category = request.GET.get('hall_category')

        missing = [k for k, v in {'date': date, 'session': session, 'hall_category': row_dept_category}.items() if not v]
        if missing:
            return JsonResponse({"staff": [], "error": f"Missing params: {', '.join(missing)}"}, status=400)

        norm_cat = (row_dept_category or '').strip().lower()

        # Busy at exact date+session
        busy_ids = list(
            InvigilationSchedule.objects
            .filter(date=date, session=session)
            .exclude(staff_id__isnull=True)
            .values_list('staff_id', flat=True)
        )

        # Same-category, active, not busy
        base = (
            Staff.objects
            .annotate(dc_norm=Lower(Trim('dept_category')))
            .filter(is_active=True, dc_norm=norm_cat)
            .exclude(staff_id__in=busy_ids)
        )

        # Capacity > 0 (DB cast)
        db_filtered = (
            base
            .annotate(
                fixed_session_int=Coalesce(Cast('fixed_session', IntegerField()), -1)
            )
            .filter(fixed_session_int__lte=-1)  # keep only fixed_session <= -1
            .order_by('staff_id')
        )

        if db_filtered.exists():
            staff = list(db_filtered.values('staff_id', 'name'))
            return JsonResponse({"staff": staff})

        # Python fallback if casting fails or returns none (handles non-numeric values safely)
        eligible = []
        for s in base.only('staff_id', 'name', 'fixed_session'):
            # Coerce fixed_session to int with default -1; exclude if > -1
            try:
                fs = int(str(s.fixed_session).strip()) if s.fixed_session is not None else -1
            except (ValueError, TypeError):
                fs = -1
            if fs <= -1:
                eligible.append({'staff_id': s.staff_id, 'name': s.name})

        return JsonResponse({"staff": eligible})

        # Final fallback: show base (same-category, free at slot) when all capacities are zero
        staff_base = list(base.order_by('staff_id').values('staff_id', 'name'))
        return JsonResponse({"staff": staff_base})

    except Exception:
        return JsonResponse({"staff": [], "error": "Internal server error"}, status=500)

def staff_edit_session(request):
    if request.method == "POST":
        staff_id = request.POST.get("staff-edit")
        date_str = request.POST.get("date-edit")
        hall_no = request.POST.get("hallno-edit")
        session = request.POST.get("session-edit")
        hall_serial = request.POST.get("serial-no-edit")

        try:
            # 📅 Parse date
            try:
                date_obj = datetime.strptime(date_str, "%b. %d, %Y").date()
            except ValueError:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 🔍 Get staff object
            staff = Staff.objects.get(staff_id=staff_id)

            # 🧠 Extract required fields
            staff_id_val = staff.staff_id
            name_val = staff.name
            designation_val = str(staff.designation)  # Convert FK to string
            staff_category_val = staff.staff_category
            dept_category_val = staff.dept_category

            print("\n===== STAFF SELECTED =====")
            print(f"Staff ID: {staff_id_val}")
            print(f"Name: {name_val}")
            print(f"Designation: {designation_val}")
            print(f"Staff Category: {staff_category_val}")
            print(f"Dept Category: {dept_category_val}")
            print(f"Hall serial: {hall_serial}")

            # 🛠️ Update InvigilationSchedule
            updated = InvigilationSchedule.objects.filter(
                date=date_obj,
                hall_no=hall_no,
                session=session,
                serial_number=hall_serial
            ).update(
                staff_id=staff_id_val,
                name=name_val,
                designation=designation_val,
                staff_category=staff_category_val,
                dept_category=dept_category_val
            )

            print(f"✅ Updated {updated} schedule record(s)")

        except Staff.DoesNotExist:
            print("❌ Staff not found for ID:", staff_id)
        except Exception as e:
            print("❌ Error in staff_edit_session:", str(e))

    return redirect("view_schedule")


def filter_options(request):
    # Dates (DateField → already date-only)
    dates_qs = (InvigilationSchedule.objects
                .exclude(date__isnull=True)
                .values_list('date', flat=True)
                .distinct()
                .order_by('date'))
    dates = [d.strftime('%Y-%m-%d') for d in dates_qs]

    # Department Category (trim + case-fold to avoid dupes like "AIDED" vs "aided")
    dept_cat_qs = (InvigilationSchedule.objects
                   .exclude(dept_category__isnull=True)
                   .exclude(dept_category='')
                   .annotate(v=Lower(Trim('dept_category')))
                   .values_list('v', flat=True)
                   .distinct()
                   .order_by('v'))
    dept_categories = list(dept_cat_qs)

    # Hall Department (trim + case-fold)
    hall_dept_qs = (InvigilationSchedule.objects
                    .exclude(hall_department__isnull=True)
                    .exclude(hall_department='')
                    .annotate(v=Lower(Trim('hall_department')))
                    .values_list('v', flat=True)
                    .distinct()
                    .order_by('v'))
    hall_departments = list(hall_dept_qs)

    return JsonResponse({
        'dates': dates,
        'dept_categories': dept_categories,
        'hall_departments': hall_departments,
    })

@require_POST
@csrf_exempt
def clear_staff_assignment(request):
    try:
        # Get data from form
        serial_number = request.POST.get('serial_number')
        date = request.POST.get('date')
        hall_no = request.POST.get('hall_no')
        session = request.POST.get('session')
        
        print(f"Clearing staff for: serial={serial_number}, date={date}, hall={hall_no}, session={session}")
        
        # Find the schedule and clear only staff-related fields
        schedule = InvigilationSchedule.objects.get(
            serial_number=serial_number,
            date=date,
            hall_no=hall_no,
            session=session
        )
        
        # Clear only the staff-related fields
        schedule.staff_id = None
        schedule.name = None
        schedule.designation = None
        schedule.staff_category = None
        schedule.dept_category = None
        schedule.save()
        
        print(f"Cleared staff fields for schedule: {schedule}")
        return JsonResponse({'success': True})
    
    except InvigilationSchedule.DoesNotExist:
        print("Schedule not found in database")
        return JsonResponse({'success': False, 'message': 'Schedule not found'})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})


