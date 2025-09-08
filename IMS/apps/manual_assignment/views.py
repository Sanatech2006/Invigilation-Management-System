from django.urls import path
from . import views
from django.db.models import Count, F

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..invigilation_schedule.models import InvigilationSchedule
from apps.staff.models import Staff
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import logging
logger = logging.getLogger(__name__)

# SAQ


def manual_assignment(request):
    """
    View for manual assignment of staff to unassigned slots
    """
    # Get staff who are active and have available sessions
    # First, get all active staff with sessions > 0
    active_staff = Staff.objects.filter(is_active=True, session__gt=0)
    
    # Calculate available sessions for each staff
    staff_with_availability = []
    for staff in active_staff:
        # Get current assignments count
        current_assignments = InvigilationSchedule.objects.filter(
            staff_id=staff.staff_id
        ).count()
        
        # Check if staff has available sessions
        available_sessions = staff.session - current_assignments
        
        if available_sessions > 0:
            staff_with_availability.append({
                'staff_id': staff.staff_id,
                'name': staff.name,
                'dept_name': staff.dept_name,
                'dept_category': staff.dept_category,
                'available_sessions': available_sessions
            })
    
    # Get unassigned slots
    unassigned_slots = InvigilationSchedule.objects.filter(
        staff_id__isnull=True
    ).values(
        'date', 
        'session', 
        'hall_no', 
        'hall_department', 
        'hall_dept_category'
    ).order_by('date', 'session', 'hall_no')
    
    # Debug output
    print(f"Available staff count: {len(staff_with_availability)}")
    print(f"Unassigned slots count: {unassigned_slots.count()}")
    
    context = {
        'unassigned_staff': staff_with_availability,
        'unassigned_slots': unassigned_slots,
    }
    
    return render(request, 'manual_assignment/manual_assignment.html', context)

@csrf_exempt
def assign_staff_to_slot(request):
    """
    API endpoint to assign staff to a slot
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        staff_id = request.POST.get('staff_id')
        date = request.POST.get('date')
        session = request.POST.get('session')
        hall_no = request.POST.get('hall_no')
        
        try:
            # Get the staff member
            staff = Staff.objects.get(staff_id=staff_id, is_active=True)
            
            # Check if staff has available sessions
            current_assignments = InvigilationSchedule.objects.filter(staff_id=staff_id).count()
            if current_assignments >= staff.session:
                return JsonResponse({
                    'success': False,
                    'message': f'Staff {staff.name} has no available sessions.'
                })
            
            # Get the slot
            slot = InvigilationSchedule.objects.get(
                date=date,
                session=session,
                hall_no=hall_no,
                staff_id__isnull=True
            )
            
            # Assign staff to slot
            slot.staff_id = staff_id
            slot.name = staff.name
            slot.designation = str(staff.designation)
            slot.staff_category = staff.staff_category
            slot.dept_category = staff.dept_category
            slot.dept_name = staff.dept_name
            slot.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully assigned {staff.name} to {hall_no} on {date} ({session})'
            })
            
        except Staff.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Staff member not found or inactive.'
            })
        except InvigilationSchedule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Slot not found or already assigned.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'{str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

@csrf_exempt
def unassign_staff_from_slot(request):
    """
    API endpoint to unassign staff from a slot
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        date = request.POST.get('date')
        session = request.POST.get('session')
        hall_no = request.POST.get('hall_no')
        
        try:
            # Get the slot
            slot = InvigilationSchedule.objects.get(
                date=date,
                session=session,
                hall_no=hall_no,
                staff_id__isnull=False
            )
            
            staff_name = slot.name
            
            # Unassign staff from slot
            slot.staff_id = None
            slot.name = None
            slot.designation = None
            slot.staff_category = None
            slot.dept_category = None
            slot.dept_name = None
            slot.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully unassigned {staff_name} from {hall_no} on {date} ({session})'
            })
            
        except InvigilationSchedule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Slot not found or already unassigned.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

@require_GET
def get_available_staff(request):
    # Get filter parameters
    date = request.GET.get('date')
    session = request.GET.get('session')
    hall_dept_category = request.GET.get('hall_category')

    if not all([date, session, hall_dept_category]):
        return JsonResponse({'staff': [], 'error': 'Missing parameters'}, status=400)
    
    # Get staff who are available for this slot
    # This should match your existing logic for finding available staff
    from django.db.models import Q
    
    # Get busy staff on this date/session
    busy_staff_ids = InvigilationSchedule.objects.filter(
        date=date,
        session=session
    ).exclude(staff_id__isnull=True).values_list('staff_id', flat=True)
    
    # Get available staff (active, with sessions, not busy, and matching category)
    available_staff = Staff.objects.filter(
        is_active=True,
        session__gt=0,
        dept_category=hall_dept_category
    ).exclude(staff_id__in=busy_staff_ids).values('staff_id', 'name')
    
    staff_list = list(available_staff)
    if not date or not session or not hall_dept_category:
        return JsonResponse({'staff': []}, status=400)
    

@require_GET
@csrf_exempt
def get_staff_assignments(request):
    staff_id = request.GET.get('staff_id')
    
    if not staff_id:
        return JsonResponse({'success': False, 'message': 'Staff ID is required'})
    
    try:
        # Get staff information
        staff = Staff.objects.get(staff_id=staff_id)
        
        # Get all assignments for this staff member
        assignments = InvigilationSchedule.objects.filter(
            staff_id=staff_id
        ).values(
            'date', 
            'session', 
            'hall_no', 
            'dept_name', 
            'dept_category'
        )
        
        assigned_sessions_count = assignments.count()
        available_sessions = max(0, staff.session - assigned_sessions_count)  # Use staff.session field
        
        return JsonResponse({
            'success': True,
            'staff_info': {
                'dept_name': staff.dept_name,
                'dept_category': staff.dept_category,
                'max_sessions': staff.session,  # Add this
                'assigned_sessions': assigned_sessions_count,  # Add this
                'available_sessions': available_sessions
            },
            'assignments': list(assignments)
        })
        
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Staff not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

# Fetch assignments for all unallotted staff (those listed in unassigned_staff logic)
@require_GET
@csrf_exempt
def get_all_staff_assignments(request):
    # Fetch assignments for all unallotted staff (those listed in unassigned_staff logic)
    # Get staff IDs who are active and have available sessions
    from apps.staff.models import Staff

    active_staff_ids = Staff.objects.filter(is_active=True, session__gt=0).values_list('staff_id', flat=True)

    # Query all assignments for these staff
    assignments = InvigilationSchedule.objects.filter(
        staff_id__in=active_staff_ids
    ).exclude(staff_id__isnull=True).values('staff_id', 'date', 'session')

    staff_assignments_map = {}
    for a in assignments:
        sid = a['staff_id'].strip()
        if sid not in staff_assignments_map:
            staff_assignments_map[sid] = []
        staff_assignments_map[sid].append({
            'date': a['date'].strftime('%Y-%m-%d'),
            'session': str(a['session']),
        })

    return JsonResponse(staff_assignments_map)

@require_GET
def get_eligible_staff(request):
    """
    Return JSON list of staff eligible for assignment on given date/session/hall_category:
    - active staff only
    - dept_category matches hall_category
    - exclude staff already assigned on this date & session
    - exclude staff who reached max sessions assigned (session field)
    """
    date = request.GET.get('date')
    session = request.GET.get('session')
    hall_category = request.GET.get('hall_category')

    if not all([date, session, hall_category]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    # Get IDs of staff assigned already on this date & session
    busy_ids = InvigilationSchedule.objects.filter(
        date=date, session=session
    ).exclude(staff_id__isnull=True).values_list('staff_id', flat=True)

    # Filter staff who are active, with matching department category, and not busy here
    staff_qs = Staff.objects.filter(
        is_active=True,
        dept_category=hall_category
    ).exclude(
        staff_id__in=busy_ids
    ).annotate(
        assigned_count=Count('invigilationschedule')
    ).filter(
        assigned_count__lt=F('session')
    )

    staff_list = [{"staff_id": s.staff_id, "name": s.name} for s in staff_qs]

    return JsonResponse({"staff": staff_list})
