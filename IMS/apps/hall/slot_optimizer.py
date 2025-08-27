from django.db.models import Count, Q, F
from apps.staff.models import Staff  # if Staff is in staff app
from ..exam_dates.models import ExamDate
from ..invigilation_schedule.models import InvigilationSchedule

def reduce_unassigned_slots(dept_category):
    """
    Optimizes unassigned slots by:
    1. Utilizing staff with remaining sessions
    2. Prioritizing session balancing
    3. Respecting all hard constraints
    """
    assignments_made = 0  # Counter for successful assignments

    # Get all unassigned slots for department
    unassigned_slots = InvigilationSchedule.objects.filter(
        staff_id__isnull=True,
        hall_dept_category__iexact=dept_category
    ).order_by('date', 'session')
    
    # Get staff with remaining capacity
    staff_with_capacity = Staff.objects.filter(
        dept_category__iexact=dept_category,
        session__gt=F('assigned_count')
    ).annotate(
        assigned_count=Count('invigilation_schedule'),
        session1=Count('invigilation_schedule', filter=Q(invigilation_schedule__session=1)),
        session2=Count('invigilation_schedule', filter=Q(invigilation_schedule__session=2))
    )
    
    total_exam_days = ExamDate.objects.count()
    
    for slot in unassigned_slots:
        # Try to find the best matching staff
        best_staff = None
        best_priority = -1  # Higher is better
        
        for staff in staff_with_capacity:
            # Skip if no remaining capacity
            if staff.assigned_count >= staff.session:
                continue
                
            # Hard Constraint 1: Department matching
            if slot.hall_department == staff.dept_name:
                continue
                
            # Hard Constraint 2: No same date+session
            if staff.invigilation_schedule.filter(
                date=slot.date,
                session=slot.session
            ).exists():
                continue
                
            # Calculate priority score (higher is better)
            priority = 0
            
            # Soft Constraint 1: Session balancing
            session_diff = staff.session1 - staff.session2
            if slot.session == 1 and session_diff >= 1:
                continue  # Skip if already has more Session 1
            elif slot.session == 2 and session_diff <= -1:
                continue  # Skip if already has more Session 2
            if slot.session == 1 and session_diff < 0:
                priority += 2  # Needs more Session 1
            elif slot.session == 2 and session_diff > 0:
                priority += 2  # Needs more Session 2
                
            # Soft Constraint 2: Avoid same-day
            if staff.assigned_count < total_exam_days:
                if staff.invigilation_schedule.filter(date=slot.date).exists():
                    priority -= 1  # Penalize same-day
                    
            # Track best candidate
            if priority > best_priority:
                best_staff = staff
                best_priority = priority
                
                
        # Assign if valid candidate found
        if best_staff:
            slot.staff_id = best_staff.staff_id
            slot.name = best_staff.name
            slot.designation = str(best_staff.designation)
            slot.staff_category = best_staff.staff_category
            slot.dept_category = best_staff.dept_category
            slot.dept_name = best_staff.dept_name
            slot.save()
            
            # Update staff counts
            best_staff.assigned_count += 1
            if slot.session == 1:
                best_staff.session1 += 1
            else:
                best_staff.session2 += 1

            assignments_made += 1  # Increment counter
            print(f"Assigned {slot.session} to {best_staff.name}")
            print(f"Total assignments in optimization: {assignments_made}")  # Summary
            
        return assignments_made
