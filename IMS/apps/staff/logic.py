from django.db.models import Sum
from datetime import datetime
from apps.staff.models import Staff
from apps.hall.models import Room # Make sure this import matches your actual model


def allocate_sessions(required_session):
    results = {}
    
    for dept_category, total_required_session in required_session.items():
        try:
            # 1. Get staff by department
            # staff_in_dept = Staff.objects.filter(dept_category=dept_category)
            staff_in_dept = Staff.objects.filter(dept_category=dept_category).order_by('date_of_joining')

            assigned_staff = staff_in_dept.filter(session=0)
            unassigned_staff = staff_in_dept.filter(fixed_session=-1)
            
            assigned_count = assigned_staff.count()
            unassigned_count = unassigned_staff.count()
            
            
            # Calculate sessions

            # fixed_session = Room.objects.filter(dept_category=dept_category).exclude(fixed_session=-1).aggregate(total=Sum('fixed_session'))['total'] or 0
          

            fixed_session = assigned_staff.aggregate(total=Sum('fixed_session'))['total'] or 0
            unallotted_session = total_required_session - fixed_session 
            print(f"DEBUG - {dept_category}: Unallotted Sessions = {unallotted_session}")

            # Edge cases
            if unallotted_session <= 0:
                results[dept_category] = {
                    'status': 'No allocation needed',
                    'reason': 'Fixed sessions already meet requirement',
                    'total_required_session': total_required_session,
                    'fixed_session': fixed_session,
                    'unallotted_session': unallotted_session
                }
                continue
                
            if unassigned_count == 0:
                results[dept_category] = {
                    'status': 'No allocation possible',
                    'reason': 'No unassigned staff available',
                    'total_required_session': total_required_session,
                    'fixed_session': fixed_session,
                    'unallotted_session': unallotted_session
                }
                continue

            # 2. Calculate base allocation and remainder
            base_allocation = unallotted_session // unassigned_count
            remainder = unallotted_session % unassigned_count

            # 3. Apply base allocation to all unassigned staff first
            # We need to evaluate the queryset before modifying it
            unassigned_staff_list = list(unassigned_staff.order_by('-date_of_joining'))
            
            for staff in unassigned_staff_list:
                staff.session = base_allocation
                staff.save()

            # 4. Distribute remainder to newest staff
            if remainder > 0:
                for i in range(remainder):
                    staff = unassigned_staff_list[i]
                    staff.session += 1  # Add one extra session
                    staff.save()

            # 5. Verify totals
            total_allocated = (
                fixed_session + 
                (base_allocation * unassigned_count) + 
                remainder  # This accounts for the extra sessions given
            )
            verification_remaining = total_required_session - total_allocated

            # Prepare allocation report
            allocation_report = [
                (staff.name, staff.date_of_joining, staff.session) 
                for staff in unassigned_staff_list
            ]
            
            # Debug output
            print(f"\n{dept_category} Allocation:")
            print(f"Total Required: {total_required_session}")
            print(f"Fixed Sessions: {fixed_session}")
            print(f"Unallotted Sessions: {unallotted_session}")
            print(f"Base Allocation: {base_allocation} per staff")
            print(f"Remainder: {remainder} extra sessions given to newest staff")
            print("Allocation Report:")
            for name, date, sess in allocation_report:
                print(f"{date}: {name} - {sess} sessions")

            results[dept_category] = {
                'status': 'Success',
                'assigned_staff': assigned_count,
                'unassigned_staff': unassigned_count,
                'base_allocation': base_allocation,
                'remainder_session': remainder,
                'allocations': allocation_report,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_required_session': total_required_session,
                'fixed_session': fixed_session,
                'unallotted_session': unallotted_session,
                'total_allocated': total_allocated,
                'verification_remaining': verification_remaining
            }

        except Exception as e:
            results[dept_category] = {
                'status': 'Failed',
                'error': str(e),
                'total_required_session': total_required_session,
                'fixed_session': fixed_session if 'fixed_session' in locals() else None,
                'unallotted_session': unallotted_session if 'unallotted_session' in locals() else None
            }
    
    return results