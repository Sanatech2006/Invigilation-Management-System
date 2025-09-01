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

# def session_staff_delete(request):
#     if request.method == "POST":
#         staff_id = request.POST.get("staff_id")
#         date_str = request.POST.get("date")
#         hall_no = request.POST.get("hall_no")
#         session = request.POST.get("session")
#         SessionSerial = request.POST.get("SessionSerial", "")

#         print("Staff ID:", staff_id)
#         print("Date:", date_str)
#         print("Hall No:", hall_no)
#         print("Session:", session)

#         # ✅ Validate and convert SessionSerial
#         if SessionSerial and SessionSerial.isdigit():
#             serial_number = int(SessionSerial)
#             print("Serial:", serial_number)
#         else:
#             print("❌ SessionSerial is missing or invalid:", SessionSerial)
#             return redirect("view_schedule")

#         # 📅 Convert date
#         try:
#             date_obj = datetime.strptime(date_str, "%b. %d, %Y").date()
#         except ValueError:
#             try:
#                 date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#             except ValueError:
#                 print("❌ Invalid date format:", date_str)
#                 return redirect("view_schedule")

#         # 🛠️ Update matching record
#         updated = InvigilationSchedule.objects.filter(
#             serial_number=serial_number,
#             staff_id=staff_id,
#             date=date_obj,
#             hall_no=hall_no,
#             session=session
#         ).update(
#             staff_id=None,
#             designation=None,
#             name=None,
#             dept_category=None,
#             double_session=False,
#             staff_category=None
#         )

#         print(f"✅ Cleared {updated} schedule record(s)")

#     return redirect("view_schedule")

def get_available_staff(request):
    try:
        date = request.GET.get('date')
        session = request.GET.get('session')
        hall_department = request.GET.get('hall_department')
        hall_category = request.GET.get('hall_category')

        # print(f"Debug - Parameters: date={date}, session={session}, hall_department={hall_department}, hall_category={hall_category}")
        print(f"Debug - Filtering assigned staff for Date: {date}, Session: {session}")

        if not date or not session or not hall_department or not hall_category:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Get staff already assigned for this date and session
        assigned_staff_ids_raw = InvigilationSchedule.objects.filter(
            date=parsed_date,
            session=session
        ).values_list('staff_id', flat=True)

        assigned_staff_ids = set(
            sid.strip().upper()
            for sid in assigned_staff_ids_raw
            if sid and sid.strip()
        )

        print(f"Debug - Assigned staff IDs: {assigned_staff_ids}")

        # First, get all staff that meet the basic criteria
        base_staff = Staff.objects.filter(
            is_active=True,
            dept_category=hall_category
        ).exclude(
            staff_id__in=assigned_staff_ids
        ).exclude(
            dept_name=hall_department
        )

        print(f"Debug - Base staff count (before max sessions check): {base_staff.count()}")

        # Now filter out staff who have reached max sessions (count all their assigned sessions)
        available_staff = []
        for staff in base_staff:
            # Count ALL sessions for this staff member in invigilation_schedule
            session_count = InvigilationSchedule.objects.filter(
                staff_id=staff.staff_id
            ).count()
            
            print(f"Debug - Staff {staff.staff_id}: max_sessions={staff.session}, current_count={session_count}")
            
            # Only include if they haven't reached their max sessions
            if session_count < staff.session:
                available_staff.append(staff)
            else:
                print(f"Debug - Excluding {staff.staff_id} (reached max sessions: {session_count}/{staff.session})")

        print(f"Debug - Final available staff count: {len(available_staff)}")

        return JsonResponse({
            "staff": [
                {"staff_id": s.staff_id, "name": s.name}
                for s in available_staff
            ]
        })

    except Exception as e:
        print("Error in get_available_staff:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": "Internal server error"}, status=500)



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
