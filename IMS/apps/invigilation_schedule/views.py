from django.db import transaction
from django.http import JsonResponse
from django.contrib import messages
from .models import InvigilationSchedule
from apps.hall.models import Room
from apps.exam_dates.models import ExamDate
from django.utils.timezone import now
import sys
from django.shortcuts import redirect
from django.shortcuts import render
from .models import InvigilationSchedule
from ..staff.models import Staff 
from django.views.decorators.http import require_GET
from datetime import datetime


def generate_schedule(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Debug start
                print("=== STARTING SCHEDULE GENERATION ===", file=sys.stderr)
                
                # 1. Get all required data
                exam_dates = list(ExamDate.objects.filter(date__gte=now().date()))
                rooms = list(Room.objects.all())
                
                if not exam_dates:
                    messages.error(request, "No future exam dates found!")
                    return redirect('generate_schedule')
                
                if not rooms:
                    messages.error(request, "No rooms found!")
                    return redirect('generate_schedule')
                
                # 2. Clear existing data
                deleted_count, _ = InvigilationSchedule.objects.all().delete()
                print(f"Deleted {deleted_count} existing records", file=sys.stderr)
                
                # 3. Create new schedules
                total_created = 0
                for exam_date in exam_dates:
                    for room in rooms:
                        staff_required = getattr(room, 'staff_required', 1)
                        total_slots = staff_required * 2
                        
                        # Create Session 1 slots
                        for _ in range(staff_required):
                            InvigilationSchedule.objects.create(
                                date=exam_date.date,
                                session='Session 1',
                                hall_no=room.hall_no,
                                hall_department=room.dept_name,
                                dept_category=room.dept_category,
                                double_session=False
                            )
                            total_created += 1
                        
                        # Create Session 2 slots
                        for _ in range(staff_required, total_slots):
                            InvigilationSchedule.objects.create(
                                date=exam_date.date,
                                session='Session 2',
                                hall_no=room.hall_no,
                                hall_department=room.dept_name,
                                dept_category=room.dept_category,
                                double_session=False
                            )
                            total_created += 1
                        
                        print(f"Created {total_slots} slots for {room.hall_no} on {exam_date.date}", file=sys.stderr)
                
                # 4. Verify creation
                db_count = InvigilationSchedule.objects.count()
                expected_count = sum(
                    getattr(room, 'staff_required', 1) * 2 * len(exam_dates)
                    for room in rooms
                )
                
                if db_count != expected_count:
                    raise ValueError(f"Created {db_count} records but expected {expected_count}")
                
                messages.success(request, 
                    f"Created {total_created} invigilation slots "
                    f"({len(exam_dates)} dates × {len(rooms)} rooms)"
                )
                return redirect('view_schedule')
                
        except Exception as e:
            messages.error(request, f"Failed to generate schedule: {str(e)}")
            return redirect('generate_schedule')
    
    return render(request, 'generate_schedule.html')

def schedule_api(request):
    try:
        schedules = InvigilationSchedule.objects.all().order_by(
            'date', 'hall_no', 'session'
        ).values(
            'id', 'date', 'session', 'hall_no', 'hall_department',
            'staff_id', 'name', 'designation', 'staff_category',
            'dept_category', 'double_session', 'dept_name',
        )
        return JsonResponse({
            'status': 'success',
            'data': list(schedules),
            'count': len(schedules)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
def view_schedule(request):  # THIS MUST EXIST
    return render(request, 'view_schedule/view_schedule.html')

def get_filter_options(request):
    dates = InvigilationSchedule.objects.values_list("date", flat=True).distinct().order_by("date")
    dept_categories = InvigilationSchedule.objects.values_list("dept_category", flat=True).distinct().order_by("dept_category")
    hall_departments = InvigilationSchedule.objects.values_list("hall_department", flat=True).distinct().order_by("hall_department")
    
    # DEBUG: Check what the query returns
    print("DEBUG: Dates:", list(dates))
    print("DEBUG: Dept categories:", list(dept_categories))
    print("DEBUG: Hall departments:", list(hall_departments))
    print("DEBUG: Hall departments count:", hall_departments.count())
    
    # Check if there are any non-empty hall departments
    non_empty_hall_depts = InvigilationSchedule.objects.exclude(hall_department__isnull=True).exclude(hall_department='').values_list("hall_department", flat=True).distinct()
    print("DEBUG: Non-empty hall departments:", list(non_empty_hall_depts))

    return JsonResponse({
        "dates": list(dates),
        "dept_categories": list(dept_categories),
        "hall_departments": list(hall_departments),
    })


# API endpoint to fetch filtered schedule data
def get_filtered_schedule(request):
    date = request.GET.get("date")
    dept_category = request.GET.get("dept_category")
    hall_department = request.GET.get("hall_department")

    qs = InvigilationSchedule.objects.all()

    if date:
        qs = qs.filter(date=date)
    if dept_category:
        qs = qs.filter(dept_category=dept_category)
    if hall_department:
        qs = qs.filter(hall_department=hall_department)

    # return only required fields
    data = list(qs.values("id", "date", "dept_category", "hall_department"))
    return JsonResponse(data, safe=False)

# @require_GET
# def get_available_staff(request):
#     # Get filter parameters
#     date = request.GET.get('date')
#     session = request.GET.get('session')
#     hall_department = request.GET.get('hall_department')
#     hall_category = request.GET.get('hall_category')
    
#     print(f"Checking availability for: date={date}, session={session}")
    
#     from .models import InvigilationSchedule, Staff
    
#     # FIRST: Get all staff who are generally available
#     all_available_staff = Staff.objects.filter(is_available=True)
#     print(f"All generally available staff: {[(s.staff_id, s.name) for s in all_available_staff]}")
    
#     # SECOND: Check which of these staff are already scheduled for this date/session
#     busy_staff_ids = []
#     for staff in all_available_staff:
#         # Check if this specific staff is already scheduled for the same date and session
#         is_already_scheduled = InvigilationSchedule.objects.filter(
#             date=date,
#             session=session,
#             staff_id=InvigilationSchedule.staff_id  # Check this specific staff ID
#         ).exists()
        
#         if is_already_scheduled:
#             busy_staff_ids.append(staff.staff_id)
#             print(f"Staff {staff.staff_id} is already scheduled on {date} session {session}")
    
#     print(f"Busy staff IDs: {busy_staff_ids}")
    
#     # FINALLY: Exclude staff who are already scheduled
#     truly_available_staff = all_available_staff.exclude(staff_id__in=busy_staff_ids)
#     print(f"Truly available staff: {[(s.staff_id, s.name) for s in truly_available_staff]}")
    
#     staff_list = [
#         {
#             'staff_id': staff.staff_id,
#             'name': staff.name
#         }
#         for staff in truly_available_staff
#     ]
    
#     return JsonResponse({'staff': staff_list})

@require_GET
def get_available_staff(request):
    # Get filter parameters
    date = request.GET.get('date')
    session = request.GET.get('session')
    hall_dept_category = request.GET.get('hall_category')
    
    print(f"🔍 === DEBUG START ===")
    print(f"📥 Input: date={date}, session={session}, hall_dept_category={hall_dept_category}")
    
    from .models import InvigilationSchedule
    
    # STEP 1: Get all staff where dept_category = hall_dept_category (REGARDLESS of staff_category)
    print(f"1️⃣ Filtering staff with dept_category = {hall_dept_category} (ignoring staff_category)...")
    category_matched_staff = InvigilationSchedule.objects.filter(
        dept_category=hall_dept_category  # ONLY check dept_category matches hall_dept_category
    ).exclude(
        staff_id__isnull=True
    ).exclude(
        staff_id__exact=''
    ).values('staff_id', 'name', 'dept_category', 'staff_category').distinct()
    
    category_matched_list = list(category_matched_staff)
    print(f"   Staff with dept_category={hall_dept_category}: {len(category_matched_list)} found")
    
    # Debug: Show staff_category values to verify both cases are included
    for staff in category_matched_list:
        status = "✅ INCLUDED" if staff['dept_category'] == hall_dept_category else "❌ EXCLUDED"
        print(f"   - {staff['staff_id']}: dept_category={staff['dept_category']}, staff_category={staff['staff_category']} {status}")
    
    # STEP 2: Get busy staff on this date/session
    print(f"2️⃣ Finding busy staff on {date}, session {session}...")
    busy_staff_ids = list(InvigilationSchedule.objects.filter(
        date=date,
        session=session
    ).exclude(staff_id__isnull=True).exclude(staff_id__exact='')
     .values_list('staff_id', flat=True).distinct())
    
    print(f"   Busy staff IDs: {busy_staff_ids}")
    
    # STEP 3: Remove busy staff from category-matched list
    print(f"3️⃣ Removing busy staff from category-matched list...")
    available_staff = [
        staff for staff in category_matched_list 
        if staff['staff_id'] not in busy_staff_ids
    ]
    
    print(f"   Available staff after removing busy: {len(available_staff)}")
    for staff in available_staff:
        print(f"   - {staff['staff_id']}: {staff['name']} (dept_category: {staff['dept_category']}, staff_category: {staff['staff_category']})")
    
    # STEP 4: Prepare final list (ONLY include staff where dept_category matches)
    staff_list = [
        {
            'staff_id': staff['staff_id'],
            'name': staff['name']
        }
        for staff in available_staff
        if staff['dept_category'] == hall_dept_category  # FINAL VERIFICATION
    ]
    
    print(f"4️⃣ Final staff list: {len(staff_list)} staff")
    print(f"📤 Returning: {staff_list}")
    print(f"🔍 === DEBUG END ===")
    
    return JsonResponse({'staff': staff_list})