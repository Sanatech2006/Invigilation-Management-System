from django.shortcuts import render
from apps.staff.models import Staff
from django.db.models import Count, Q
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.staff.models import Staff
from apps.hall.models import Room 



from django.shortcuts import render, redirect
from apps.staff.models import Staff
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.hall.models import Room  # Assuming Room is your hall model


def reports_view(request):
    staff_id = request.session.get('staff_id')
    welcome_message = "WELCOME, Guest"
    role = None
    schedules = []

    if staff_id:
        try:
            staff = Staff.objects.get(staff_id=staff_id)
            staff_name = staff.name
            role = staff.role
            designation = getattr(staff, 'designation', '')

            if role == 3:
                # For HOD (role 3), redirect or call hod_view
                return hod_view(request)

            if role == 1:
                welcome_message = f"WELCOME, {staff_name}"
            elif role == 2:
                welcome_message = f"WELCOME, Squad Team, {staff_name}"
            elif role == 4:
                welcome_message = f"WELCOME, Staff Member, {staff_name}, {staff_id}"
                # Fetch invigilation schedule data for role 4
                schedules = InvigilationSchedule.objects.filter(
                    staff_id=staff.staff_id
                ).values('date', 'session', 'hall_no', 'hall_department')

        except Staff.DoesNotExist:
            pass  # Keep defaults

    context = {
        'welcome_message': welcome_message,
        'schedules': schedules,
        'role': role,
    }
    return render(request, 'reports/staff.html', context)


def hod_view(request):
    staff_id = request.session.get('staff_id')
    try:
        hod = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        hod = None

    if not hod:
        return render(request, 'error.html', {'message': 'Unauthorized or invalid user'})

    dept_name = hod.dept_name

    # Summary information
    
    total_staff = Staff.objects.filter(
        dept_name=dept_name,
        dept_category=hod.dept_category
    ).count()
    
    total_halls = Room.objects.filter(
        dept_name=dept_name,
        dept_category=hod.dept_category
    ).count()

    total_sessions = InvigilationSchedule.objects.filter(
        hall_dept_category=hod.dept_category,
        hall_department=dept_name
        ).count()



    # My Schedule (logged-in HOD schedule)
    my_schedule = InvigilationSchedule.objects.filter(staff_id=hod.staff_id).values(
        'date', 'session', 'hall_no', 'hall_department'
    ).order_by('date', 'session')

    # Staff Details
    staff_details = list(Staff.objects.filter(
        dept_name=dept_name,
        dept_category=hod.dept_category
    ).values(
        'staff_id', 'name', 'date_of_joining', 'mobile'
    ).order_by('date_of_joining', 'name'))

    for staff in staff_details:
        date_val = staff.get('date_of_joining')
        if date_val:
            # Convert to string if not already, take first 10 chars (YYYY-MM-DD)
            staff['date_of_joining'] = str(date_val)[:10]
        else:
            staff['date_of_joining'] = ''

    # hall_details = Room.objects.filter(
    #     dept_name=dept_name,
    #     dept_category=hod.dept_category
    # ).values(
    #     'hall_no', 'strength'
    # ).distinct().order_by('hall_no')

    hall_details = Room.objects.filter(
        dept_name=dept_name,
        dept_category=hod.dept_category
    ).values(
        'hall_no', 'strength', 'staff_required'
    ).distinct().order_by('hall_no')


    dept_staff_ids = Staff.objects.filter(dept_name=dept_name).values_list('staff_id', flat=True)
  
    hall_schedule_qs = InvigilationSchedule.objects.filter(
        hall_department=dept_name,
        hall_dept_category=hod.dept_category  # add department category filter
    ).values(
        'hall_no', 'date', 'session', 'staff_id', 'hall_department'
    ).order_by('date', 'hall_no')

    # Fetch staff info for related staff_ids
    staff_ids = {entry['staff_id'] for entry in hall_schedule_qs if entry['staff_id']}
    staff_map = {s.staff_id: s for s in Staff.objects.filter(staff_id__in=staff_ids)}

    # Enrich hall_schedule with staff data
    hall_schedule = []
    for entry in hall_schedule_qs:
        staff_obj = staff_map.get(entry['staff_id'])
        entry['staff_name'] = staff_obj.name if staff_obj else 'Unknown'
        entry['staff_mobile'] = staff_obj.mobile if staff_obj else ''
        entry['staff_dept'] = staff_obj.dept_name if staff_obj else 'Unknown'  # Add staff's own department
        hall_schedule.append(entry)

    # Staff Schedule - fetch without join

    staff_schedule_qs = InvigilationSchedule.objects.filter(
        dept_name=dept_name,
        dept_category=hod.dept_category
    ).values(
        'staff_id', 'date', 'session', 'hall_no', 'hall_department'
    ).order_by('date', 'staff_id')


    # Fetch staff info for related staff_ids
    staff_ids_sched = {item['staff_id'] for item in staff_schedule_qs if item['staff_id']}
    staff_map_sched = {s.staff_id: s for s in Staff.objects.filter(staff_id__in=staff_ids_sched)}

    # Enrich staff_schedule with staff data
    staff_schedule = []
    for item in staff_schedule_qs:
        staff_obj = staff_map_sched.get(item['staff_id'])
        item['staff_name'] = staff_obj.name if staff_obj else 'Unknown'
        item['staff_mobile'] = staff_obj.mobile if staff_obj else ''
        staff_schedule.append(item)

    context = {
        'welcome_message': f"Welcome  {hod.name},    Department of {hod.dept_name}",
        'total_staff': total_staff,
        'total_halls': total_halls,
        'total_sessions': total_sessions,
        'my_schedule': my_schedule,
        'staff_details': staff_details,
        'hall_details': hall_details,
        'hall_schedule': hall_schedule,
        'staff_schedule': staff_schedule,
    }

    return render(request, 'reports/hod.html', context)
def admin_view(request):
    # Overall Summary
    total_staff = Staff.objects.count()
    total_halls = Room.objects.count()
    total_sessions = InvigilationSchedule.objects.count()
    unassigned_sessions = InvigilationSchedule.objects.filter(staff_id__isnull=True).count()
    unassigned_halls = Room.objects.filter(staff_allotted="Not Allotted").count()

    # Department-Wise Summary
    from django.db.models import Count, Sum, Q

    departments = Staff.objects.values('dept_name').annotate(
        staff_count=Count('id', distinct=True),
    ).order_by('dept_name')

    hall_dept = Room.objects.values('dept_name').annotate(
        halls_allotted=Count('hall_no', distinct=True),
        sessions_scheduled=Sum('required_session'),
    )

    # Map department -> halls/counts for quick reference
    hall_dept_map = {h['dept_name']: h for h in hall_dept}
    dept_summary = []
    for idx, dept in enumerate(departments, 1):
        name = dept['dept_name']
        halls = hall_dept_map.get(name, {}).get('halls_allotted', 0)
        sessions = hall_dept_map.get(name, {}).get('sessions_scheduled', 0)
        # Count unassigned sessions for each department
        dept_rooms = Room.objects.filter(dept_name=name)
        room_halls = list(dept_rooms.values_list('hall_no', flat=True))
        unassigned = InvigilationSchedule.objects.filter(
            hall_department=name, staff_id__isnull=True
        ).count()
        dept_summary.append({
            "s_no": idx,
            "dept": name,
            "no_of_staff": dept['staff_count'],
            "halls_allotted": halls,
            "sessions_scheduled": sessions,
            "unassigned_sessions": unassigned
        })

    # Staff Workload Distribution
    all_staff = Staff.objects.all().order_by('dept_name', 'name')
    staff_workload = []
    for idx, staff in enumerate(all_staff, 1):
        num_sessions = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).count()
        num_halls = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).values('hall_no').distinct().count()
        staff_workload.append({
            "s_no": idx,
            "staff_id": staff.staff_id,
            "staff_name": staff.name,
            "department": staff.dept_name,
            "num_sessions": num_sessions,
            "num_halls": num_halls,
            "mobile_no": staff.mobile
        })

    # Hall Utilization Report
    all_halls = Room.objects.all().order_by('hall_no')
    hall_utilization = []
    for idx, hall in enumerate(all_halls, 1):
        assigned_strength = InvigilationSchedule.objects.filter(hall_no=hall.hall_no).count()
        capacity = hall.strength or 1  # Avoid division by zero
        percent_util = (assigned_strength / capacity) * 100 if capacity else 0
        hall_utilization.append({
            "s_no": idx,
            "hall_no": hall.hall_no,
            "capacity": capacity,
            "assigned_strength": assigned_strength,
            "percent_utilization": round(percent_util, 2),
            "department": hall.dept_name
        })

    # Conflict / Overlap Report
    conflicts = []
    qs = InvigilationSchedule.objects.values(
        'staff_id', 'date', 'session'
    ).annotate(
        halls=Count('hall_no')
    ).filter(
        halls__gt=1, staff_id__isnull=False
    ).order_by('date', 'session', 'staff_id')

    for idx, conflict in enumerate(qs, 1):
        staff = Staff.objects.filter(staff_id=conflict['staff_id']).first()
        conflicting_halls = list(InvigilationSchedule.objects.filter(
            staff_id=conflict['staff_id'], date=conflict['date'], session=conflict['session']
        ).values_list('hall_no', flat=True))
        conflicts.append({
            "s_no": idx,
            "staff_id": conflict['staff_id'],
            "staff_name": staff.name if staff else 'Unknown',
            "department": staff.dept_name if staff else 'Unknown',
            "date": conflict['date'],
            "session": conflict['session'],
            "assigned_halls": ', '.join(map(str, conflicting_halls))
        })

    # Master Invigilation Schedule (College-Wide)
    master_schedule = InvigilationSchedule.objects.select_related(None).order_by('date', 'session', 'hall_no')
    master_rows = []
    staff_map = {s.staff_id: s for s in Staff.objects.filter(staff_id__in=master_schedule.values_list('staff_id', flat=True))}
    for idx, entry in enumerate(master_schedule, 1):
        staff_obj = staff_map.get(entry.staff_id)
        master_rows.append({
            "s_no": idx,
            "date": entry.date,
            "session": entry.session,
            "hall_no": entry.hall_no,
            "staff_name": staff_obj.name if staff_obj else '-',
            "department": staff_obj.dept_name if staff_obj else '-',
            "mobile_no": staff_obj.mobile if staff_obj else '-',
        })

    context = {
        "total_staff": total_staff,
        "total_halls": total_halls,
        "total_sessions": total_sessions,
        "unassigned_sessions": unassigned_sessions,
        "unassigned_halls": unassigned_halls,
        "dept_summary": dept_summary,
        "staff_workload": staff_workload,
        "hall_utilization": hall_utilization,
        "conflicts": conflicts,
        "master_schedule": master_rows,
    }
    return render(request, "reports/admin.html", context)
