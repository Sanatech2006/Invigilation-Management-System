from django.shortcuts import render
from apps.staff.models import Staff
from django.db.models import Count, Q
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.staff.models import Staff
from apps.hall.models import Room 
from django.db.models import OuterRef, Subquery, Count, IntegerField, F, Sum
from django.db.models.functions import Coalesce
from collections import defaultdict
from django.shortcuts import render, redirect
from apps.staff.models import Staff
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.hall.models import Room  # Assuming Room is your hall model
from apps.exam_dates.models import ExamDate



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
            
            # --- REMOVED THE IF ROLE == 3 REDIRECT FROM HERE ---
            
            welcome_message = f"WELCOME, {staff_name}"
            
            # Fetch ONLY the personal schedule for whoever is logged in (Role 3 or 4)
            schedules = (
                InvigilationSchedule.objects
                .filter(staff_id=staff.staff_id)
                .values('date', 'session', 'hall_no', 'hall_department')
                .order_by('date', 'session')
            )

        except Staff.DoesNotExist:
            pass 

    context = {
        'welcome_message': welcome_message,
        'schedules': schedules,
        'role': role,
    }
    # This now always shows the personal staff page (staff.html)
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
    ).order_by('date', 'hall_no', 'session')

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
        # 'welcome_message': f"Welcome  {hod.name},    Department of {hod.dept_name}",
        'welcome_message': f"Welcome {hod.name}<br>Department of {hod.dept_name}",

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

# This is ONLY for "My Schedule"
def personal_schedule_view(request):
    staff_id = request.session.get('staff_id')
    # Just get this one person's schedule
    my_data = InvigilationSchedule.objects.filter(staff_id=staff_id)
    
    return render(request, 'reports/re.html', {'my_schedule': my_data})

def admin_view(request):
    total_staff = Staff.objects.count()
    total_halls = Room.objects.count()
    total_sessions = InvigilationSchedule.objects.count()
    unassigned_sessions = InvigilationSchedule.objects.filter(staff_id__isnull=True).count()
    unassigned_halls = Room.objects.filter(staff_allotted="Not Allotted").count()

    assigned_sessions_subquery = InvigilationSchedule.objects.filter(
        staff_id=OuterRef('staff_id')
    ).values('staff_id').annotate(
        cnt=Count('serial_number')
    ).values('cnt')

    staff_with_counts = Staff.objects.annotate(
        assigned_count=Coalesce(Subquery(assigned_sessions_subquery, output_field=IntegerField()), 0)
    ).filter(
        assigned_count__lt=F('session')
    )

    unassigned_staff_count = staff_with_counts.count()

    departments = Staff.objects.values('dept_name').annotate(
        staff_count=Count('id', distinct=True),
    ).order_by('dept_name')

    hall_dept = Room.objects.values('dept_name').annotate(
        halls_allotted=Count('hall_no', distinct=True),
        sessions_scheduled=Sum('required_session'),
    )

    hall_dept_map = {h['dept_name']: h for h in hall_dept}
    dept_summary = []
    for idx, dept in enumerate(departments, 1):
        name = dept['dept_name']
        halls = hall_dept_map.get(name, {}).get('halls_allotted', 0)
        sessions = hall_dept_map.get(name, {}).get('sessions_scheduled', 0)
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
    conflicts_qs = (
    InvigilationSchedule.objects
    .values('staff_id', 'date', 'session')
    .annotate(hall_count=Count('hall_no'))
    .filter(hall_count__gt=1, staff_id__isnull=False)
)

    staff_ids_with_conflict = set([c['staff_id'] for c in conflicts_qs])

    conflict_staff = (
        Staff.objects
        .filter(staff_id__in=staff_ids_with_conflict)
        .values('staff_id', 'name', 'dept_category')
    )

    conflict_report = defaultdict(list)
    for staff in conflict_staff:
        conflict_report[staff['dept_category']].append({
            'staff_id': staff['staff_id'],
            'name': staff['name'],
            'dept_category': staff['dept_category'],
        })

    # Format for template (list by category)
    conflict_report_rows = []
    for category in ['AIDED', 'SFM', 'SFW']:
        staff_list = conflict_report.get(category, [])
        conflict_report_rows.append({
            'category': category,
            'conflicts': staff_list
        })
    master_schedule = InvigilationSchedule.objects.select_related(None).order_by('date', 'session', 'hall_no')
    staff_map = {s.staff_id: s for s in Staff.objects.filter(staff_id__in=master_schedule.values_list('staff_id', flat=True))}
    master_rows = []
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

    # Sessions Report
    categories = ['AIDED', 'SFM', 'SFW']
    sessions_report = []
    for category in categories:
        total_cat = InvigilationSchedule.objects.filter(hall_dept_category=category).count()
        assigned_cat = InvigilationSchedule.objects.filter(hall_dept_category=category).exclude(staff_id__isnull=True).count()
        unassigned_cat = total_cat - assigned_cat
        sessions_report.append({
            'category': category,
            'assigned': assigned_cat,
            'unassigned': unassigned_cat,
            'total': total_cat,
        })

    # Staff Report
    staff_report = []
    for category in categories:
        staff_in_cat = Staff.objects.filter(dept_category=category, is_active=True)
        total_staff_cat = staff_in_cat.count()

        assigned_sessions_subquery = InvigilationSchedule.objects.filter(
            staff_id=OuterRef('staff_id')
        ).values('staff_id').annotate(
            cnt=Count('serial_number')
        ).values('cnt')

        staff_with_counts = staff_in_cat.annotate(
            assigned_count=Coalesce(Subquery(assigned_sessions_subquery, output_field=IntegerField()), 0)
        )

        unassigned_staff_count_cat = staff_with_counts.filter(assigned_count__lt=F('session')).count()
        assigned_staff_count_cat = total_staff_cat - unassigned_staff_count_cat

        staff_report.append({
            'category': category,
            'assigned': assigned_staff_count_cat,
            'unassigned': unassigned_staff_count_cat,
            'total': total_staff_cat,
        })
        categories = ['AIDED', 'SFM', 'SFW']

    # Dates Report: assigned sessions per dept_category by date
    categories = ['AIDED', 'SFM', 'SFW']
    dates = ExamDate.objects.all().order_by('date')
    dates_report = []
    for idx, exam_date in enumerate(dates, 1):
            # Total sessions per department category for this date
            total_counts = (
                InvigilationSchedule.objects
                .filter(date=exam_date.date)
                .values('hall_dept_category')
                .annotate(total_sessions=Count('serial_number'))
            )
            assigned_counts = (
                InvigilationSchedule.objects
                .filter(date=exam_date.date, staff_id__isnull=False)
                .values('hall_dept_category')
                .annotate(assigned_sessions=Count('serial_number'))
            )

            # Build dictionaries for quick lookup
            total_dict = {c['hall_dept_category']: c['total_sessions'] for c in total_counts}
            assigned_dict = {c['hall_dept_category']: c['assigned_sessions'] for c in assigned_counts}

            # Prepare per-date/per-category result with assigned, unassigned, and total
            row = {
                's_no': idx,
                'date': exam_date.date,
            }
            for cat in categories:
                total = total_dict.get(cat, 0)
                assigned = assigned_dict.get(cat, 0)
                unassigned = total - assigned
                row[cat] = {
                    'assigned': assigned,
                    'unassigned': unassigned,
                    'total': total,
                }
            dates_report.append(row)
        
    context = {
        "total_staff": total_staff,
        "total_halls": total_halls,
        "total_sessions": total_sessions,
        "unassigned_sessions": unassigned_sessions,
        "unassigned_halls": unassigned_halls,
        "unassigned_staff_count": unassigned_staff_count,
        "dept_summary": dept_summary,
        "staff_workload": staff_workload,
        "hall_utilization": hall_utilization,
        "conflicts": conflicts,
        "master_schedule": master_rows,
        "sessions_report": sessions_report,
        "staff_report": staff_report,
        "conflict_report_rows": conflict_report_rows,
        "dates_report": dates_report,

    }

    return render(request, "reports/admin.html", context)