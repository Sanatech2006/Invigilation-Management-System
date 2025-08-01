from django.db.models import Sum, Count
from datetime import datetime
from apps.staff.models import Staff   # Make sure this import is correct

def allocate_sessions(total_staff_required):
    """
    Allocate sessions to staff with session=-1 based on department categories
    total_staff_required: Dictionary {dept_category: required_sessions}
    Returns dictionary with allocation results
    """
    results = {}
    
    for dept_category, required_sessions in total_staff_required.items():
        try:
            # Filter staff by department category
            staff_in_dept = Staff.objects.filter(dept_category=dept_category)
            
            # Identify assigned and unassigned staff
            assigned_staff = staff_in_dept.filter(session__gt=-1)
            unassigned_staff = staff_in_dept.filter(session=-1).order_by('date_of_joining')
            
            assigned_count = assigned_staff.count()
            unassigned_count = unassigned_staff.count()
            
            # Calculate fixed sessions sum
            fixed_sessions = assigned_staff.aggregate(total=Sum('session'))['total'] or 0
            
            # Determine remaining sessions
            remaining_sessions = required_sessions - fixed_sessions
            
            if remaining_sessions <= 0:
                results[dept_category] = {
                    'status': 'No allocation needed',
                    'reason': 'Fixed sessions already meet requirement'
                }
                continue
                
            if unassigned_count == 0:
                results[dept_category] = {
                    'status': 'No allocation possible',
                    'reason': 'No unassigned staff (session=-1)'
                }
                continue
                
            # Calculate base allocation and remainder
            base_allocation = remaining_sessions // unassigned_count
            remainder = remaining_sessions % unassigned_count
            
            # Apply allocations
            updated_count = 0
            for i, staff in enumerate(unassigned_staff):
                # Junior staff (later joining dates) get the remainder
                allocation = base_allocation + (1 if i < remainder else 0)
                
                if allocation > 0:
                    staff.session = allocation
                    staff.save()
                    updated_count += 1
            
            results[dept_category] = {
                'status': 'Success',
                'assigned_staff': assigned_count,
                'unassigned_staff': unassigned_count,
                'fixed_sessions': fixed_sessions,
                'remaining_sessions': remaining_sessions,
                'base_allocation': base_allocation,
                'remainder': remainder,
                'updated_count': updated_count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            results[dept_category] = {
                'status': 'Failed',
                'error': str(e)
            }
    
    return results