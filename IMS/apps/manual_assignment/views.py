from django.urls import path
from . import views
from django.db import transaction
from django.db.models import Count, F
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..invigilation_schedule.models import InvigilationSchedule
from apps.staff.models import Staff
from apps.exam_dates.models import ExamDate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
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
        'total_unassigned_sessions': sum(s['available_sessions'] for s in staff_with_availability),
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

@csrf_exempt
@require_POST
def auto_assign_staff(request):
    """
    Fallback allocation for Manual Assignment using Maximum Bipartite Matching.

    Finds the MAXIMUM valid assignment of unassigned hall slots to available
    staff using augmenting-path DFS (Hopcroft-Karp style), which naturally
    handles chain reassignments / swapping during the current fallback run.

    Hard constraints enforced (NEVER violated):
      HC1  dept_category match  — staff.dept_category == slot.hall_dept_category
      HC2  No own-department    — staff.dept_name != slot.hall_department
      HC3  No date+session clash — (staff_id, date, session) must be unique
      HC4  Capacity             — total assignments < staff.session

    Soft constraints (used only for ordering, never to exclude):
      SC1  Session balancing    — prefer assigning to staff's under-represented
                                   session (Session 1 vs Session 2)
      SC2  Same-day spread      — prefer staff not already on same exam date

    The algorithm considers ONLY assignments made during this fallback run
    for chain reassignment. Existing pre-run assignments are never disturbed.
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    try:
        from django.db.models import Count, Q, F
        from django.db.models.functions import Coalesce
        from apps.exam_dates.models import ExamDate

        total_exam_days = ExamDate.objects.count()

        # ── 1. Load unassigned slots ──────────────────────────────────────────
        unassigned_slots = list(
            InvigilationSchedule.objects.filter(staff_id__isnull=True)
            .exclude(hall_dept_category__isnull=True)
            .exclude(hall_dept_category='')
            .order_by('hall_dept_category', 'date', 'session', 'serial_number')
        )

        if not unassigned_slots:
            return JsonResponse({
                'success': True,
                'message': 'No unassigned hall slots found.',
                'assignments_made': 0,
                'remaining_unassigned': 0,
            })

        # ── 2. Load staff with remaining capacity ─────────────────────────────
        # Build a dict: staff_id -> staff object with live counts
        from apps.staff.models import Staff as _Staff  # already imported at module level
        staff_objects = {}
        for st in Staff.objects.filter(is_active=True, session__gt=0):
            n = InvigilationSchedule.objects.filter(staff_id=st.staff_id).count()
            if n < st.session:
                # Annotate counts in-memory so we can adjust as we match
                st._assigned_count = n
                st._s1_count = InvigilationSchedule.objects.filter(
                    staff_id=st.staff_id, session='1').count()
                st._s2_count = InvigilationSchedule.objects.filter(
                    staff_id=st.staff_id, session='2').count()
                # Pre-load existing (date, session) pairs to avoid repeated DB hits
                st._occupied = set(
                    InvigilationSchedule.objects.filter(staff_id=st.staff_id)
                    .values_list('date', 'session')
                )
                staff_objects[st.staff_id] = st

        if not staff_objects:
            remaining_slots = list(unassigned_slots)
            remaining_halls = len(remaining_slots)
            remaining_sessions = len(set((s.date, s.session) for s in remaining_slots))
            msg = (
                f"No Further Assignments Possible\n\n"
                f"{remaining_halls} Hall{'s' if remaining_halls != 1 else ''} and "
                f"{remaining_sessions} Session{'s' if remaining_sessions != 1 else ''} remain unassigned.\n\n"
                f"Click Staff Swap to find eligible swap candidates and complete the remaining assignments."
            )
            return JsonResponse({
                'success': True,
                'message': msg,
                'assignments_made': 0,
                'remaining_unassigned': remaining_halls,
                'remaining_sessions': remaining_sessions,
            })

        # ── 3. Build candidate lists per slot (adjacency list) ────────────────
        #
        # For the matching graph:
        #   Left  = slots (indexed 0..N-1)
        #   Right = staff-capacity units  (each staff with remaining=R has R units)
        #
        # We model multi-capacity staff by allowing the matching algorithm to
        # assign the same staff to multiple slots, tracked via _assigned_count
        # and _occupied.  We do NOT explode into individual capacity units;
        # instead the DFS naturally handles it through the _assigned_count guard.

        def _is_eligible(staff, slot, extra_occupied=None):
            """Return True iff all hard constraints pass for this pair.
            extra_occupied: set of (date, session) pairs tentatively assigned
                            to this staff in the current matching run."""
            # HC4: capacity (using in-memory counter)
            if staff._assigned_count >= staff.session:
                return False
            # HC1: dept_category match
            if staff.dept_category.lower() != slot.hall_dept_category.lower():
                return False
            # HC2: no own-department
            if staff.dept_name == slot.hall_department:
                return False
            # HC3: date+session clash (pre-run assignments)
            key = (slot.date, slot.session)
            if key in staff._occupied:
                return False
            # HC3: clash with tentative in-run assignments
            if extra_occupied and key in extra_occupied:
                return False
            return True

        def _soft_score(staff, slot):
            """Higher score = better candidate (used only for ordering)."""
            score = 0
            # Prefer staff with more remaining capacity (even distribution)
            remaining = staff.session - staff._assigned_count
            score += remaining * 10
            # Session balance bonus
            diff = staff._s1_count - staff._s2_count
            if slot.session == '1' and diff < 0:
                score += 5
            elif slot.session == '2' and diff > 0:
                score += 5
            # Same-day penalty
            same_day = any(d == slot.date for d, _ in staff._occupied)
            if same_day and staff._assigned_count < total_exam_days:
                score -= 3
            return score

        # Build adjacency list for each slot
        slot_candidates = []  # parallel list to unassigned_slots
        for slot in unassigned_slots:
            candidates = [
                st for st in staff_objects.values()
                if _is_eligible(st, slot)
            ]
            # Sort by soft score descending so DFS tries best candidates first
            candidates.sort(key=lambda st: _soft_score(st, slot), reverse=True)
            slot_candidates.append(candidates)

        # ── 4. Maximum Bipartite Matching via augmenting-path DFS ────────────
        #
        # matching[slot_idx] = staff object currently matched to this slot
        # (None if unmatched)
        n_slots = len(unassigned_slots)
        matching = [None] * n_slots  # slot_idx -> staff obj

        # For each staff, track which slot indices they are currently matched to
        # so we can find augmenting paths through them.
        from collections import defaultdict
        staff_matched_slots = defaultdict(set)  # staff_id -> set of slot_idx

        # In-run tentative occupancy per staff (accumulated across matched slots)
        # We maintain this separately from staff._occupied (pre-run DB data).
        staff_inrun_occupied = defaultdict(set)  # staff_id -> set of (date, session)

        def _try_assign(slot_idx, visited_slots):
            """
            Attempt to find an augmenting path starting from slot_idx.
            visited_slots: set of slot indices already visited in this DFS call
                           (prevents infinite loops).
            Returns True if slot_idx was successfully matched.
            """
            if slot_idx in visited_slots:
                return False
            visited_slots.add(slot_idx)

            slot = unassigned_slots[slot_idx]
            for staff in slot_candidates[slot_idx]:
                # Re-check HC4 with current in-memory counter
                if staff._assigned_count >= staff.session:
                    continue
                # Re-check HC3 with in-run tentative occupancy
                key = (slot.date, slot.session)
                if key in staff_inrun_occupied[staff.staff_id]:
                    continue
                # HC1 and HC2 were already checked in slot_candidates; no need to re-check

                # This staff is directly available — match them
                matching[slot_idx] = staff
                staff_matched_slots[staff.staff_id].add(slot_idx)
                staff_inrun_occupied[staff.staff_id].add(key)
                staff._assigned_count += 1
                if slot.session == '1':
                    staff._s1_count += 1
                else:
                    staff._s2_count += 1
                return True

            # No direct assignment worked.  Try augmenting through existing matches:
            # For each candidate staff member, check if they are already matched
            # to another slot; if we can re-match that other slot to someone else,
            # we free this staff for the current slot.
            for staff in slot_candidates[slot_idx]:
                if staff._assigned_count >= staff.session:
                    # Staff is at capacity.  Try to free one of their matched slots
                    # by finding an alternative match for it.
                    key = (slot.date, slot.session)
                    if key in staff_inrun_occupied[staff.staff_id]:
                        # Staff already has this date+session — can't help
                        continue

                    # Find a matched slot this staff holds that we can re-route
                    freed = False
                    for other_idx in list(staff_matched_slots[staff.staff_id]):
                        other_slot = unassigned_slots[other_idx]
                        other_key = (other_slot.date, other_slot.session)

                        # Tentatively remove this staff from other_idx
                        staff_matched_slots[staff.staff_id].discard(other_idx)
                        staff_inrun_occupied[staff.staff_id].discard(other_key)
                        staff._assigned_count -= 1
                        if other_slot.session == '1':
                            staff._s1_count -= 1
                        else:
                            staff._s2_count -= 1
                        matching[other_idx] = None

                        # Try to find an alternative for other_idx
                        if _try_assign(other_idx, visited_slots):
                            # Success — staff is now free (one slot freed), match to current
                            matching[slot_idx] = staff
                            staff_matched_slots[staff.staff_id].add(slot_idx)
                            staff_inrun_occupied[staff.staff_id].add(key)
                            staff._assigned_count += 1
                            if slot.session == '1':
                                staff._s1_count += 1
                            else:
                                staff._s2_count += 1
                            freed = True
                            break
                        else:
                            # Restore — couldn't re-route, put staff back on other_idx
                            matching[other_idx] = staff
                            staff_matched_slots[staff.staff_id].add(other_idx)
                            staff_inrun_occupied[staff.staff_id].add(other_key)
                            staff._assigned_count += 1
                            if other_slot.session == '1':
                                staff._s1_count += 1
                            else:
                                staff._s2_count += 1

                    if freed:
                        return True

            return False  # No augmenting path found

        total_matched = 0
        for slot_idx in range(n_slots):
            if _try_assign(slot_idx, set()):
                total_matched += 1

        # ── 5. Persist matches to database ────────────────────────────────────
        assignments_made = 0
        for slot_idx, staff in enumerate(matching):
            if staff is None:
                continue
            slot = unassigned_slots[slot_idx]
            # Final hard-constraint safety re-check before writing
            real_count = InvigilationSchedule.objects.filter(
                staff_id=staff.staff_id).count()
            clash = InvigilationSchedule.objects.filter(
                staff_id=staff.staff_id,
                date=slot.date,
                session=slot.session,
            ).exists()
            if real_count >= staff.session or clash:
                continue  # Integrity guard — skip if DB state changed concurrently

            InvigilationSchedule.objects.filter(
                serial_number=slot.serial_number
            ).update(
                staff_id=staff.staff_id,
                name=staff.name,
                designation=str(staff.designation),
                staff_category=staff.staff_category,
                dept_category=staff.dept_category,
                dept_name=staff.dept_name,
            )
            assignments_made += 1

        # ── 6. Update double_session flags ───────────────────────────────────
        if assignments_made > 0:
            _update_double_session_flags()

        # ── 7. Build detailed impossibility report for remaining slots ────────
        remaining_slots = list(
            InvigilationSchedule.objects.filter(staff_id__isnull=True)
            .exclude(hall_dept_category__isnull=True)
            .exclude(hall_dept_category='')
        )
        remaining = len(remaining_slots)

        # Explain why each remaining slot is impossible (for clarity in response)
        impossible_reasons = {}
        for slot in remaining_slots:
            reasons = set()
            for st in staff_objects.values():
                if st.dept_category.lower() != slot.hall_dept_category.lower():
                    reasons.add('no_matching_category_staff')
                    continue
                if st.dept_name == slot.hall_department:
                    reasons.add('all_eligible_staff_in_own_dept')
                    continue
                real_count = InvigilationSchedule.objects.filter(
                    staff_id=st.staff_id).count()
                if real_count >= st.session:
                    reasons.add('all_eligible_staff_at_capacity')
                    continue
                clash = InvigilationSchedule.objects.filter(
                    staff_id=st.staff_id,
                    date=slot.date,
                    session=slot.session,
                ).exists()
                if clash:
                    reasons.add('all_eligible_staff_clash_on_date_session')
            impossible_reasons[slot.serial_number] = sorted(reasons)

        # Build a concise summary
        reason_summary = {}
        for sn, reasons in impossible_reasons.items():
            key = ', '.join(reasons) if reasons else 'unknown'
            reason_summary[key] = reason_summary.get(key, 0) + 1

        remaining_halls = remaining
        remaining_sessions = len(set((s.date, s.session) for s in remaining_slots))

        # ── 8. Compose response ───────────────────────────────────────────────
        if assignments_made > 0:
            msg = (
                f'Successfully assigned {assignments_made} '
                f'slot{"s" if assignments_made != 1 else ""}.'
            )
            if remaining > 0:
                msg += (
                    f' {remaining} hall{"s" if remaining != 1 else ""} remain '
                    f'unassigned (constraint-blocked: {reason_summary}).'
                )
        elif remaining > 0:
            msg = (
                f"No Further Assignments Possible\n\n"
                f"{remaining_halls} Hall{'s' if remaining_halls != 1 else ''} and "
                f"{remaining_sessions} Session{'s' if remaining_sessions != 1 else ''} remain unassigned.\n\n"
                f"Click Staff Swap to find eligible swap candidates and complete the remaining assignments."
            )
        else:
            msg = 'All slots already assigned.'

        return JsonResponse({
            'success': True,
            'message': msg,
            'assignments_made': assignments_made,
            'remaining_unassigned': remaining,
            'remaining_sessions': remaining_sessions,
            'impossibility_reasons': reason_summary,
        })

    except Exception as e:
        logger.error('Error in auto_assign_staff: %s', str(e), exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def _update_double_session_flags():
    """
    Recalculate the double_session boolean on all InvigilationSchedule records.
    Mirrors the double_session() function in apps/hall/views.py.
    A staff member has double_session=True for a given date if they have
    assignments in both Session 1 and Session 2 on that date.
    """
    from django.db.models import Count

    session_counts = (
        InvigilationSchedule.objects
        .values('date', 'staff_id')
        .annotate(session_count=Count('session', distinct=True))
        .filter(staff_id__isnull=False)
    )

    double_session_staff = {
        (entry['date'], entry['staff_id'])
        for entry in session_counts
        if entry['session_count'] == 2
    }

    schedules = list(InvigilationSchedule.objects.all())
    for record in schedules:
        record.double_session = (
            (record.date, record.staff_id) in double_session_staff
        )

    InvigilationSchedule.objects.bulk_update(schedules, ['double_session'])


# ==============================================================================
# STAFF SWAP WORKFLOW VIEWS & APIS
# ==============================================================================

def staff_swap(request):
    """
    View for Manual Assignment -> Staff Swap page.
    Displays list of unallotted staff members and unallotted hall assignments.
    """
    active_staff = Staff.objects.filter(is_active=True, session__gt=0)
    
    staff_with_availability = []
    for staff in active_staff:
        current_assignments = InvigilationSchedule.objects.filter(
            staff_id=staff.staff_id
        ).count()
        available_sessions = staff.session - current_assignments
        if available_sessions > 0:
            staff_with_availability.append({
                'staff_id': staff.staff_id,
                'name': staff.name,
                'dept_name': staff.dept_name,
                'staff_category': staff.staff_category,
                'dept_category': staff.dept_category,
                'available_sessions': available_sessions
            })
    
    unassigned_slots = InvigilationSchedule.objects.filter(
        staff_id__isnull=True
    ).values(
        'serial_number',
        'date', 
        'session', 
        'hall_no', 
        'hall_department', 
        'hall_dept_category'
    ).order_by('date', 'session', 'hall_no')
    
    context = {
        'unassigned_staff': staff_with_availability,
        'unassigned_slots': unassigned_slots,
    }
    
    return render(request, 'manual_assignment/staff_swap.html', context)


@require_GET
def get_swap_unassigned_halls(request):
    """
    Fetch unassigned hall slots filtered strictly by Staff A's dept_category.
    Used exclusively in Staff Swap workflow.
    """
    staff_id = request.GET.get('staff_id')
    dept_category = request.GET.get('dept_category')
    
    if not staff_id and not dept_category:
        return JsonResponse({'success': False, 'message': 'staff_id or dept_category required'}, status=400)
    
    if staff_id and not dept_category:
        try:
            staff = Staff.objects.get(staff_id=staff_id, is_active=True)
            dept_category = staff.dept_category
        except Staff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Staff member not found'}, status=404)
            
    if not dept_category:
        return JsonResponse({'success': True, 'unassigned_slots': []})
        
    unassigned_slots = InvigilationSchedule.objects.filter(
        staff_id__isnull=True,
        hall_dept_category__iexact=dept_category.strip()
    ).values(
        'serial_number',
        'date',
        'session',
        'hall_no',
        'hall_department',
        'hall_dept_category'
    ).order_by('date', 'session', 'hall_no')
    
    slots_data = []
    for slot in unassigned_slots:
        slots_data.append({
            'serial_number': slot['serial_number'],
            'hall_no': slot['hall_no'],
            'date': slot['date'].strftime('%Y-%m-%d'),
            'session': slot['session'],
            'hall_department': slot['hall_department'],
            'hall_dept_category': slot['hall_dept_category'],
        })
        
    return JsonResponse({
        'success': True,
        'dept_category': dept_category,
        'unassigned_slots': slots_data
    })


@require_GET
def get_swap_available_dates(request):
    """
    Step 3: Identify available dates for selected unallotted Staff A.
    Retrieve exam dates on which Staff A is available/free.
    """
    staff_id = request.GET.get('staff_id')
    if not staff_id:
        return JsonResponse({'success': False, 'message': 'Staff ID required'}, status=400)
    
    try:
        staff = Staff.objects.get(staff_id=staff_id, is_active=True)
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Staff member not found'}, status=404)
    
    # Get distinct exam dates
    all_dates = list(ExamDate.objects.order_by('date').values_list('date', flat=True))
    if not all_dates:
        all_dates = list(
            InvigilationSchedule.objects.values_list('date', flat=True).distinct().order_by('date')
        )
    
    available_dates = []
    for d in all_dates:
        # Check if staff has assignments on this date
        has_assignment = InvigilationSchedule.objects.filter(staff_id=staff_id, date=d).exists()
        
        # Staff is available on date d only if they do not already have an assignment on this date
        if not has_assignment:
            available_dates.append({
                'date_str': d.strftime('%Y-%m-%d'),
                'display': d.strftime('%Y-%m-%d (%A)')
            })
            
    return JsonResponse({'success': True, 'available_dates': available_dates})


@require_GET
def find_eligible_swap_staff(request):
    """
    Step 4 & Step 5: Find eligible already-assigned staff members (Staff B) for swap on selected date.
    Checks all 5 eligibility conditions:
    Condition 1: Same Staff Category (Staff B.staff_category == Staff A.staff_category)
    Condition 2: Staff B must have an existing assignment (Slot 2)
    Condition 3: Slot 2 must NOT be in Staff A's parent department (Staff A.dept_name != Slot 2.hall_department)
    Condition 4: Candidate Staff B must be free in BOTH sessions on Slot 1's date (Date D1)
    Condition 5: All existing constraints pass (dept_category match, no own-dept for Staff B in Slot 1, Staff A free on Slot 2's session, capacity limits).
    """
    staff_a_id = request.GET.get('staff_a_id')
    slot1_serial = request.GET.get('slot1_serial')
    selected_date = request.GET.get('selected_date')

    if not all([staff_a_id, slot1_serial, selected_date]):
        return JsonResponse({'success': False, 'message': 'Missing required parameters'}, status=400)

    try:
        staff_a = Staff.objects.get(staff_id=staff_a_id, is_active=True)
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Selected unallotted staff member not found.'})

    try:
        slot1 = InvigilationSchedule.objects.get(serial_number=slot1_serial, staff_id__isnull=True)
    except InvigilationSchedule.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Selected unallotted hall assignment not found.'})

    # Check Staff A capacity
    staff_a_assignments = InvigilationSchedule.objects.filter(staff_id=staff_a.staff_id).count()
    if staff_a_assignments >= staff_a.session:
        return JsonResponse({'success': False, 'message': 'Selected staff member has reached maximum assigned session capacity.'})

    # Find already-assigned slots on selected_date (Date D2)
    slot2_candidates = InvigilationSchedule.objects.filter(
        date=selected_date,
        staff_id__isnull=False
    ).exclude(staff_id='')

    eligible_candidates = []

    for slot2 in slot2_candidates:
        staff_b_id = slot2.staff_id
        if staff_b_id == staff_a_id:
            continue

        try:
            staff_b = Staff.objects.get(staff_id=staff_b_id, is_active=True)
        except Staff.DoesNotExist:
            continue

        # Condition 1 — Same Staff Category
        if staff_b.staff_category != staff_a.staff_category:
            continue

        # Condition 2 — Existing Assignment (Slot 2) is valid - slot2 exists

        # Condition 3 — Slot 2 hall department must NOT be Staff A's parent department
        if staff_a.dept_name and slot2.hall_department and staff_a.dept_name.strip().lower() == slot2.hall_department.strip().lower():
            continue

        # Condition 4 — Candidate Staff B must be free in BOTH sessions on Date D1 (slot1.date)
        staff_b_on_d1 = InvigilationSchedule.objects.filter(
            staff_id=staff_b_id,
            date=slot1.date
        ).exists()
        if staff_b_on_d1:
            continue

        # Condition 5 — All existing constraints must pass:
        # a) Staff B for Slot 1: dept_category match
        if slot1.hall_dept_category and staff_b.dept_category:
            if staff_b.dept_category.strip().lower() != slot1.hall_dept_category.strip().lower():
                continue

        # b) Staff B for Slot 1: No own department rule
        if staff_b.dept_name and slot1.hall_department and staff_b.dept_name.strip().lower() == slot1.hall_department.strip().lower():
            continue

        # c) Staff A for Slot 2: dept_category match
        if slot2.hall_dept_category and staff_a.dept_category:
            if staff_a.dept_category.strip().lower() != slot2.hall_dept_category.strip().lower():
                continue

        # d) Staff A for Slot 2: Staff A free on Slot 2's date & session
        staff_a_clash_slot2 = InvigilationSchedule.objects.filter(
            staff_id=staff_a_id,
            date=slot2.date,
            session=slot2.session
        ).exists()
        if staff_a_clash_slot2:
            continue

        eligible_candidates.append({
            'staff_b_id': staff_b.staff_id,
            'staff_b_name': staff_b.name,
            'staff_b_category': staff_b.staff_category,
            'staff_b_dept': staff_b.dept_name,
            'slot2_serial': slot2.serial_number,
            'slot2_hall': slot2.hall_no,
            'slot2_date': slot2.date.strftime('%Y-%m-%d'),
            'slot2_session': slot2.session,
            'slot2_dept': slot2.hall_department,
            'slot2_category': slot2.hall_dept_category,
        })

    if not eligible_candidates:
        return JsonResponse({
            'success': True,
            'eligible_staff': [],
            'message': 'No valid staff swap found.'
        })

    return JsonResponse({
        'success': True,
        'eligible_staff': eligible_candidates,
        'message': f'Found {len(eligible_candidates)} eligible staff candidate(s) for swap.'
    })


@csrf_exempt
@require_POST
def perform_staff_swap(request):
    """
    Step 6, 7, 8: Perform the Staff Swap and Reassignment in an atomic transaction.
    """
    staff_a_id = request.POST.get('staff_a_id')
    slot1_serial = request.POST.get('slot1_serial')
    staff_b_id = request.POST.get('staff_b_id')
    slot2_serial = request.POST.get('slot2_serial')

    if not all([staff_a_id, slot1_serial, staff_b_id, slot2_serial]):
        return JsonResponse({'success': False, 'message': 'Missing required parameters for swap.'}, status=400)

    try:
        with transaction.atomic():
            staff_a = Staff.objects.get(staff_id=staff_a_id, is_active=True)
            staff_b = Staff.objects.get(staff_id=staff_b_id, is_active=True)
            slot1 = InvigilationSchedule.objects.select_for_update().get(serial_number=slot1_serial)
            slot2 = InvigilationSchedule.objects.select_for_update().get(serial_number=slot2_serial)

            # Defensive verification checks before committing
            if slot1.staff_id:
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Slot 1 is already assigned.'})

            if slot2.staff_id != staff_b_id:
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Slot 2 assignment state changed.'})

            # Check Category
            if staff_a.staff_category != staff_b.staff_category:
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Staff categories do not match.'})

            # Parent Dept check: Staff A cannot go to Slot 2 if Slot 2 is Staff A's own dept
            if staff_a.dept_name and slot2.hall_department and staff_a.dept_name.strip().lower() == slot2.hall_department.strip().lower():
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Parent department restriction for Staff A.'})

            # Staff B cannot go to Slot 1 if Slot 1 is Staff B's own dept
            if staff_b.dept_name and slot1.hall_department and staff_b.dept_name.strip().lower() == slot1.hall_department.strip().lower():
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Parent department restriction for Staff B.'})

            # Staff B must have no existing assignment on Date D1
            if InvigilationSchedule.objects.filter(staff_id=staff_b_id, date=slot1.date).exclude(serial_number=slot2_serial).exists():
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Candidate staff is busy on unallotted date.'})

            # Staff A must have no clash on Slot 2 date/session
            if InvigilationSchedule.objects.filter(staff_id=staff_a_id, date=slot2.date, session=slot2.session).exists():
                return JsonResponse({'success': False, 'message': 'No valid staff swap found. Unallotted staff has a session clash.'})

            # Step 6: Move Staff B to Slot 1 (Original Unallotted Hall Assignment)
            slot1.staff_id = staff_b.staff_id
            slot1.name = staff_b.name
            slot1.designation = str(staff_b.designation)
            slot1.staff_category = staff_b.staff_category
            slot1.dept_category = staff_b.dept_category
            slot1.dept_name = staff_b.dept_name
            slot1.save()

            # Step 7: Assign Staff A to Slot 2 (Released by Staff B)
            slot2.staff_id = staff_a.staff_id
            slot2.name = staff_a.name
            slot2.designation = str(staff_a.designation)
            slot2.staff_category = staff_a.staff_category
            slot2.dept_category = staff_a.dept_category
            slot2.dept_name = staff_a.dept_name
            slot2.save()

            # Step 8: Update double_session flags
            _update_double_session_flags()

            return JsonResponse({
                'success': True,
                'message': f'Staff swap successful! {staff_b.name} assigned to Hall {slot1.hall_no} on {slot1.date} ({slot1.session}), and {staff_a.name} assigned to Hall {slot2.hall_no} on {slot2.date} ({slot2.session}).'
            })

    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Staff member not found.'})
    except InvigilationSchedule.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Slot not found.'})
    except Exception as e:
        logger.error('Error during staff swap: %s', str(e), exc_info=True)
        return JsonResponse({'success': False, 'message': f'No valid staff swap found. Error: {str(e)}'})



