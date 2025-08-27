from django.contrib.auth.decorators import login_required
from apps.common.decorators import role_required
from apps.invigilation_schedule.models import InvigilationSchedule

from django.shortcuts import render
import logging


@role_required([4, 3])  # Staff and HOD
def own_schedule(request):
       
    staff_id = request.session.get('staff_id')  # or request.user.staff_id if available

    if not staff_id:
        # Handle missing staff_id in session gracefully
        return render(request, 'reports/staff.html', {'schedule': [], 'message': 'Staff ID not found in session.'})

    # Query the invigilation_schedule filtered by staff_id, ordered by date/session
    schedule_qs = InvigilationSchedule.objects.filter(staff_id=staff_id).order_by('date', 'session')

    # Only fetch necessary fields to optimize query
    schedule = schedule_qs.values('date', 'session', 'hall_no', 'hall_department')

    # Pass the schedule list to template context
    context = {
        'schedule': schedule,
    }

    return render(request, 'reports/staff.html', context)

@login_required
@role_required([3])  # Only HOD
def visiting_staff(request):
    # Staff visiting HOD's department for invigilation
    pass

@login_required
@role_required([3])  # Only HOD
def department_staff_out(request):
    # Staff from HOD's department going to other depts for invigilation
    pass

@login_required
@role_required([2])  # Only Squad
def squad_schedule(request):
    # Fetch squad schedule from Squad table for logged-in squad user
    pass

@login_required
@role_required([1])  # Only Admin
def schedule_report(request):
    # Admin-wide schedule report
    pass

@login_required
@role_required([1])  # Only Admin
def squad_report(request):
    # Admin-wide squad report
    pass
