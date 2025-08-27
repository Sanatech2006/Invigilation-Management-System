from django.db.models import Count, Q, F, Subquery, OuterRef
from apps.staff.models import Staff
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule

def reduce_unassigned_slots(dept_category):
    """
    Optimizes unassigned slots without relying on 'id' field or foreign key relations
    """
    # 1. Get all unassigned slots for the department
    unassigned_slots = InvigilationSchedule.objects.filter(
        staff_id__isnull=True,
        hall_dept_category__iexact=dept_category
    ).order_by('date', 'session')
    
    # 2. Get staff with remaining capacity using serial_number as identifier
    assignment_counts = InvigilationSchedule.objects.filter(
        staff_id=OuterRef('staff_id')
    ).values('staff_id').annotate(
        total=Count('serial_number'),  # Using serial_number instead of id
        session1=Count('serial_number', filter=Q(session=1)),
        session2=Count('serial_number', filter=Q(session=2))
    ).values('total', 'session1', 'session2')
    
    # Get staff with capacity
    staff_with_capacity = Staff.objects.filter(
        dept_category__iexact=dept_category,
        is_active=True,
        session__gt=0
    ).annotate(
        assigned_count=Subquery(assignment_counts.values('total')[:1], default=0),
        session1_count=Subquery(assignment_counts.values('session1')[:1], default=0),
        session2_count=Subquery(assignment_counts.values('session2')[:1], default=0)
    ).filter(
        session__gt=F('assigned_count')
    )
    
    total_exam_days = ExamDate.objects.count()
    assignments_made = 0
    
    # for slot in unassigned_slots:
    #     best_staff = None
    #     best_priority = -1
        
    #     for staff in staff_with_capacity:
    #         # Skip if no remaining capacity
    #         if staff.assigned_count >= staff.session:
    #             continue
                
    #         # Hard Constraint 1: Department matching
    #         if slot.hall_department == staff.dept_name:
    #             continue
                
    #         # Hard Constraint 2: No same date+session
    #         existing_assignments = InvigilationSchedule.objects.filter(
    #             staff_id=staff.staff_id,
    #             date=slot.date,
    #             session=slot.session
    #         ).exists()
    #         if existing_assignments:
    #             continue
                
    #         # Calculate priority score
    #         priority = 0
            
    #         # Session balancing
    #         session_diff = staff.session1_count - staff.session2_count
    #         if slot.session == 1 and session_diff < 0:
    #             priority += 2
    #         elif slot.session == 2 and session_diff > 0:
    #             priority += 2
                
    #         # Same-day avoidance
    #         if staff.assigned_count < total_exam_days:
    #             same_day = InvigilationSchedule.objects.filter(
    #                 staff_id=staff.staff_id,
    #                 date=slot.date
    #             ).exists()
    #             if same_day:
    #                 priority -= 1
                    
    #         # Track best candidate
    #         if priority > best_priority:
    #             best_staff = staff
    #             best_priority = priority
                
    #     # Make assignment if valid candidate found
    #     if best_staff:
    #         # Fresh capacity check
    #         fresh_count = InvigilationSchedule.objects.filter(
    #         staff_id=best_staff.staff_id
    #         ).count()
    
    #         if fresh_count < best_staff.session:  # Only assign if under capacity
    #             InvigilationSchedule.objects.filter(serial_number=slot.serial_number).update(
    #             staff_id=best_staff.staff_id,
    #             name=best_staff.name,
    #             designation=str(best_staff.designation),
    #             staff_category=best_staff.staff_category,
    #             dept_category=best_staff.dept_category,
    #             dept_name=best_staff.dept_name
    #             )
    #             assignments_made += 1

    # return assignments_made

    for slot in unassigned_slots:
        best_staff = None
        for attempt in range(3):  # 3 attempts: strict → relaxed → minimal
            best_priority = -1
            for staff in staff_with_capacity:
                if staff.session <= 3:
                    continue  # Skip during auto-phase
                # Hard constraints (unchanged)
                if (staff.assigned_count >= staff.session or
                    slot.hall_department == staff.dept_name or
                    InvigilationSchedule.objects.filter(
                        staff_id=staff.staff_id,
                        date=slot.date,
                        session=slot.session
                    ).exists()):
                    continue
                
                # Soft constraints (attempt-based)
                session_diff = staff.session1_count - staff.session2_count
                same_day = InvigilationSchedule.objects.filter(
                    staff_id=staff.staff_id,
                    date=slot.date
                ).exists()
                
                if attempt == 0:  # Strict
                    if not ((slot.session == 1 and session_diff < 0) or 
                           (slot.session == 2 and session_diff > 0)):
                        continue
                    if same_day and staff.assigned_count < total_exam_days:
                        continue
                elif attempt == 1:  # Relaxed
                    if same_day and staff.assigned_count < total_exam_days:
                        continue
                # attempt=2 (minimal) has no soft constraints
                
                priority = 0  # Not used in minimal mode
                if priority > best_priority:
                    best_staff = staff
                    best_priority = priority
            
            if best_staff:
                break  # Exit attempt loop if found
                
        if best_staff:  # Original assignment logic
            fresh_count = InvigilationSchedule.objects.filter(
                staff_id=best_staff.staff_id
            ).count()
            if fresh_count < best_staff.session:
                InvigilationSchedule.objects.filter(serial_number=slot.serial_number).update(
                    staff_id=best_staff.staff_id,
                    name=best_staff.name,
                    designation=str(best_staff.designation),
                    staff_category=best_staff.staff_category,
                    dept_category=best_staff.dept_category,
                    dept_name=best_staff.dept_name
                )
                assignments_made += 1

    return assignments_made
