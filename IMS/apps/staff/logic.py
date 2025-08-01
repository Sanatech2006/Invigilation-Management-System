from django.db.models import Sum
from datetime import datetime
from apps.staff.models import Staff

def allocate_sessions(total_staff_required):
    results = {}
    
    for dept_category, required_sessions in total_staff_required.items():
        try:
            # Get staff data
            staff_in_dept = Staff.objects.filter(dept_category=dept_category)
            assigned_staff = staff_in_dept.filter(session__gt=-1)
            unassigned_staff = staff_in_dept.filter(session=-1)
            
            # Calculate session requirements
            assigned_count = assigned_staff.count()
            unassigned_count = unassigned_staff.count()
            fixed_sessions = assigned_staff.aggregate(total=Sum('session'))['total'] or 0
            remaining_sessions = required_sessions - fixed_sessions

            # Edge cases
            if remaining_sessions <= 0:
                results[dept_category] = {
                    'status': 'No allocation needed',
                    'reason': 'Fixed sessions already meet requirement'
                }
                continue
                
            if unassigned_count == 0:
                results[dept_category] = {
                    'status': 'No allocation possible',
                    'reason': 'No unassigned staff available'
                }
                continue

            # Strict equal distribution
            sessions_per_staff = remaining_sessions // unassigned_count
            
            if sessions_per_staff == 0:
                results[dept_category] = {
                    'status': 'Cannot allocate equally',
                    'reason': f'Need {remaining_sessions} more sessions for equal distribution'
                }
                continue

            # Apply equal allocation
            for staff in unassigned_staff:
                staff.session = sessions_per_staff
                staff.save()

            results[dept_category] = {
                'status': 'Success',
                'assigned_staff': assigned_count,
                'unassigned_staff': unassigned_count,
                'sessions_per_staff': sessions_per_staff,
                'leftover_sessions': remaining_sessions % unassigned_count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            results[dept_category] = {
                'status': 'Failed',
                'error': str(e)
            }
    
    return results