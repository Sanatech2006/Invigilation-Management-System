import pandas as pd
from django.shortcuts import render,redirect
from .models import Room
from django.db.models import Sum
from django.db.models import Sum, Count
from staff.logic import allocate_sessions
from django.http import HttpResponse
from openpyxl import Workbook
from apps.staff.models import Staff
from django.utils import timezone
import datetime
from collections import defaultdict
from ..exam_dates.models import ExamDate
from ..invigilation_schedule.models import InvigilationSchedule
import random
import openpyxl
from django.db.models import Q, F, Count, Case, When
from django.contrib import messages
import pandas as pd
from io import BytesIO
from django.http import HttpResponse

from .slot_optimizer import reduce_unassigned_slots
from .reduce_unassigned_slots import reduce_unassigned_slots

def is_assignment_allowed(current_s1, current_s2, new_session):
    """
    Checks assignment rules in reverse order:
    1. Allowed (best) → 2. Avoidable → 3. Blocked (worst)
    """
    difference = (current_s1 - current_s2)
    
    # Calculate projected difference
    projected_diff = difference + 1 if new_session == 1 else difference - 1

    # 1. First check for ideal cases (0 or ±1 difference)
    if abs(projected_diff) <= 1:
        return True, "Allowed (imbalance ≤ 1)"  # ✅ Best case

    # 2. Then check avoidable cases (±2 difference)
    elif abs(projected_diff) == 2:
        return True, "Allowed but avoid (imbalance 2)"  # ⚠️ Good but not ideal

    # 3. Finally handle blocked cases (≥±3 difference)
    else:
        return False, "Blocked (imbalance ≥ 3)"  # ❌ Worst case

def hall_management(request):
    print("\n===== NEW REQUEST =====")  # Debug
    print(f"Request method: {request.method}")  # Debug
    
    # Initialize context with all required data
    context = {
        'rooms': Room.objects.all(),
        'blocks': Room.objects.values_list('block', flat=True).distinct(),
        'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
        'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
    }

    if request.method == "POST":
        print("\nPOST request received")  # Debug
        print("Request.FILES contents:", request.FILES)  # Debug
        print("Request.POST contents:", request.POST)  # Debug
        
        if 'file' not in request.FILES:
            print("\nERROR: No file found in request.FILES")  # Debug
            context['error'] = "No file was uploaded"
            return render(request, 'hall/hall_management.html', context)
            
        excel_file = request.FILES['file']
        print(f"\nFile detected: {excel_file.name}")  # Debug
        print(f"File size: {excel_file.size} bytes")  # Debug
        print(f"Content type: {excel_file.content_type}")  # Debug
        
        try:
            print("\nAttempting to read Excel file...")  # Debug
            df = pd.read_excel(excel_file)
            # Delete existing rooms BEFORE processing new data
            if Room.objects.exists():  # Safety check
                deleted_count = Room.objects.all().delete()[0]
            print("SUCCESS: File read successfully")  # Debug
            print("Columns in file:", df.columns.tolist())  # Debug
            print("First row sample:", df.iloc[0].to_dict() if not df.empty else "Empty DataFrame")  # Debug

            processed = 0
            for _, row in df.iterrows():
                try:
                    hall_no = str(row['hall_no']).strip()
                    if not hall_no:
                        continue
                    
                    # Calculate staff_required based on strength
                    strength = int(row.get('strength', 0))
                    staff_required = 1 if strength < 55 else 2
                    # Get days value from Excel (default to 1 if not provided)
                    days = int(row.get('days', 1))
                    
                    # Calculate required_session
                    sessions = 2  # Assuming 2 sessions per day as per your requirement
                    required_session = staff_required * sessions * days
                    
                    
                    Room.objects.create(
                        hall_no=hall_no,
                        dept_category=str(row.get('dept_category', '')),
                        dept_name=str(row.get('dept_name', '')),
                        strength=strength,
                        days=int(row.get('days', 0)),
                        staff_required=staff_required,
                        required_session=required_session,
                        block="-",
                        staff_allotted="Not Allotted",
                        benches=0,
                    )
                    processed += 1
                except Exception as e:
                    print(f"Row processing error: {e}")  # Debug
                    continue

            context['message'] = f"Successfully processed {processed} records"
            # Refresh data
            context.update({
                'rooms': Room.objects.all(),
                'blocks': Room.objects.values_list('block', flat=True).distinct(),
                'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
                'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
            })
            
        except Exception as e:
            print(f"\nERROR processing file: {str(e)}")  # Debug
            context['error'] = f"Error processing file: {str(e)}"

    return render(request, 'hall/hall_management.html', context)

def hall_list(request):
    rooms = Room.objects.all()
    return render(request, 'hall/hall_list.html', {'halls': rooms})

def generate_schedule(request):
    


    CATEGORIES = ['AIDED', 'SFM', 'SFW']
    
    # # Get room data
    room_data = Room.objects.values('dept_category').annotate(
        total_sessions=Sum('required_session')
    ).order_by('dept_category')
    
    # # Get staff data
    staff_data = Staff.objects.values('dept_category').annotate(
        total_staff=Count('id')
    ).order_by('dept_category')
    
    room_dict = {item['dept_category'].upper(): item for item in room_data}
    staff_dict = {item['dept_category'].upper(): item for item in staff_data}
    
    # Prepare schedule data for display
    schedule_data = []
    for category in CATEGORIES:
        sessions = room_dict.get(category, {}).get('total_sessions', 0)
        staff_count = staff_dict.get(category, {}).get('total_staff', 0)
        
        schedule_data.append({
            'category': category,
            'total_sessions': sessions,
            'staff_count': staff_count
        })

    required_session = {
        item['dept_category']: item['total_sessions']
        for item in room_data
    }
    
    # # Handle allocation if requested
    allocation_results = None
    if request.method == 'POST' and 'allocate_sessions' in request.POST:
        allocation_results = allocate_sessions(required_session)

    # Calculate total sessions required by category
    categories = Room.objects.values('dept_category').annotate(
        total_sessions=Sum('required_session')
    ).order_by('dept_category')
    # i=1
    # for hall in halls:
    #     print(i,hall)
    #     i=i+1

    # # Get staff counts with case-insensitive matching  
    staff_counts = {
        'Aided': Staff.objects.filter(dept_category__iexact='aided').count(),
        'SFM': Staff.objects.filter(dept_category__iexact='sfm').count(),
        'SFW': Staff.objects.filter(dept_category__iexact='sfw').count()
    }
    
    # # Format the data for display
    
    # # Format the data for display with staff counts
    schedule_data = []
    for item in categories:
            dept = item['dept_category']
            # Normalize department name for lookup
            lookup_dept = 'Aided' if dept.lower() == 'aided' else dept.upper()
            schedule_data.append({
                'category': dept,
                'total_sessions': item['total_sessions'],
                'staff_count': staff_counts.get(lookup_dept, 0),
                'allocation_status': allocation_results[dept]['status'] if allocation_results else None
            })

    context = {
        'schedule_data': schedule_data,
        'categories': CATEGORIES,
        'allocation_results': allocation_results
    }

    return render(request, 'hall/generate_schedule.html', context)


def export_schedule_excel(request):
    # Create a workbook and add worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Staff Schedule"
    
    # Add column headers
    headers = [
        "Staff ID",
        "Name", 
        "Department",
        "Department Category",
        "Sessions",
        "Join Date",
        "Fixed session",
    ]
    ws.append(headers)
    
    # Get all staff data with correct comma separation
    staff_data = Staff.objects.all().values_list(
        'staff_id',      # Staff ID
        'name',          # Name
        'dept_name',     # Department
        'dept_category', # Department Category
        'session',       # Sessions
        'date_of_joining', # Join Date
        'fixed_session',
    )
    
    # Add data rows
    for staff in staff_data:
        ws.append(staff)
    
    # Format the date fields
    for row in ws.iter_rows(min_row=2):
        if len(row) > 5 and isinstance(row[5].value, (datetime.date, datetime.datetime)):  # Date of Joining column (6th column)
            row[5].number_format = 'YYYY-MM-DD'
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f"staff_schedule_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response




def generate_session(request):
    InvigilationSchedule.objects.all().delete()
    if request.method == "POST":
        print("this is the route")
        halls = Room.objects.all().values() 
        dates=ExamDate.objects.all()
        print("dates",dates)

        # Assuming you already have dates and halls loaded

        for date in dates:
            for hall in halls:
                total = hall['staff_required'] * 2
                for i in range(total):
                    session_number = "1" if i < total // 2 else "2"
                    # print("gsfd",date.date)

                    InvigilationSchedule.objects.create(
                        date=date.date,
                        session=session_number,
                        hall_no=hall['hall_no'],
                        hall_department=hall['dept_name'],
                        hall_dept_category=hall['dept_category'],
                        #set later
                        dept_category="None",
                        staff_id=None,
                        name=None,
                        designation=None,
                        staff_category=None,
                        double_session=False
                    )
                    # print("gsfd",date.date)
        return redirect('generate_schedule')


# SAQ TEST CODE 
def assign_staff(request):
    if request.method != 'POST':
        return redirect('generate_schedule')

    DEPT_CATEGORIES = ['AIDED', 'SFM', 'SFW']
    
    for dept_category in DEPT_CATEGORIES:
        print(f"\n=== PROCESSING {dept_category} DEPARTMENT ===")
        
        # 1. Prepare staff data with remaining capacity
        staff_queryset = Staff.objects.filter(
            is_active=True,
            session__gt=0,
            dept_category__iexact=dept_category
        ).order_by('-session')
        
        staff_list = []
        for staff in staff_queryset:
            assigned_count = InvigilationSchedule.objects.filter(
                staff_id=staff.staff_id
            ).count()
            staff_list.append({
                'staff_id': staff.staff_id,
                'name': staff.name,
                'designation': str(staff.designation),
                'staff_category': staff.staff_category,
                'dept_category': staff.dept_category,
                'dept_name': staff.dept_name,
                'session': staff.session,
                'remaining': staff.session - assigned_count
            })

        # 2. Get all unassigned slots for this department
        unassigned_slots = InvigilationSchedule.objects.filter(
            staff_id__isnull=True,
            hall_dept_category__iexact=dept_category
        ).order_by('date', 'session')

        total_slots = unassigned_slots.count()   # ✅ Add this line

        # 3. Perform assignment
        unassigned_count = 0

        total_slots = unassigned_slots.count()   # ✅ Add this line

        # for slot in unassigned_slots:
        for i, slot in enumerate(unassigned_slots, start=1):   # <-- changed loop # ✅ Add this line
            print(f"Progress: {i}/{total_slots}")               # ✅ Add this line
            assigned = False
            
            # Try to find eligible staff with remaining capacity
            for staff in staff_list:
                if staff['remaining'] <= 0:
                    continue
                # if staff['session'] <= 3:
                #     continue  # Skip during auto-phase
                    
                # Hard constraint: Same department check
                if slot.hall_department == staff['dept_name']:
                    continue
                    
                # Hard constraint: Same date+session check
                if InvigilationSchedule.objects.filter(
                    staff_id=staff['staff_id'],
                    date=slot.date,
                    session=slot.session
                ).exists():
                    continue
                    
                # Soft constraint: Same-day avoidance (only if sessions < total days)
                total_exam_days = ExamDate.objects.latest('day_no').day_no
                if staff['remaining'] < total_exam_days:
                    if InvigilationSchedule.objects.filter(
                        staff_id=staff['staff_id'],
                        date=slot.date
                    ).exists():
                        continue  # Skip but may retry later
                                  
                # Soft constraint: Session balancing
                session_counts = InvigilationSchedule.objects.filter(
                    staff_id=staff['staff_id']
                ).aggregate(
                    session1=Count(Case(When(session=1, then=1))),
                    session2=Count(Case(When(session=2, then=1)))
                )
                
                allowed, reason = is_assignment_allowed(
                    current_s1=session_counts['session1'],
                    current_s2=session_counts['session2'],
                    new_session=slot.session
                )
                
                if not allowed:
                    continue  # Skip blocked assignments
                elif "avoid" in reason:
                    pass  # Skip if already has more Session 2 assignments

                # Make the assignment
                slot.staff_id = staff['staff_id']
                slot.name = staff['name']
                slot.designation = staff['designation']
                slot.staff_category = staff['staff_category']
                slot.dept_category = staff['dept_category']
                slot.dept_name = staff['dept_name']
                slot.save()
                staff['remaining'] -= 1
                assigned = True
                break
            
            if not assigned:
                unassigned_count += 1
            
        # 4. Generate result messages
        total_slots = InvigilationSchedule.objects.filter(
            hall_dept_category__iexact=dept_category
        ).count()
        
        assigned_slots = total_slots - unassigned_count
        remaining_staff = sum(1 for s in staff_list if s['remaining'] > 0)

        if unassigned_count > 0:
            assignments_made = reduce_unassigned_slots(dept_category)
            messages.info(
                request,
                f"{dept_category}: Optimization assigned {assignments_made} slots. "
                f"{unassigned_count - assignments_made} still unassigned."
            )

            # Phase III saq
            # ================================================
            # PHASE 3: Reassignment with Your Exact Constraints
            # ================================================
            remaining_slots = InvigilationSchedule.objects.filter(
                staff_id__isnull=True,
                hall_dept_category__iexact=dept_category
            ).order_by('date', 'session')

            if remaining_slots.exists():
                print(f"🔍 PHASE 3: Processing {remaining_slots.count()} unassigned slots")
                
                for slot in remaining_slots:
                    # FIRST: Try direct assignment to staff with remaining capacity
                    direct_assignment = False
                    for staff_data in staff_list:
                        if staff_data['remaining'] <= 0:
                            continue
                        
                        # Hard Constraints
                        if slot.hall_department == staff_data['dept_name']:
                            continue
                        if InvigilationSchedule.objects.filter(
                            staff_id=staff_data['staff_id'],
                            date=slot.date,
                            session=slot.session
                        ).exists():
                            continue
                        
                        # Soft Constraints
                        total_exam_days = ExamDate.objects.latest('day_no').day_no
                        if staff_data['remaining'] < total_exam_days:
                            if InvigilationSchedule.objects.filter(
                                staff_id=staff_data['staff_id'],
                                date=slot.date
                            ).exists():
                                continue
                        session_counts = InvigilationSchedule.objects.filter(
                            staff_id=staff_data['staff_id']
                        ).aggregate(
                            session1=Count(Case(When(session=1, then=1))),
                            session2=Count(Case(When(session=2, then=1)))
                        )
                        allowed, _ = is_assignment_allowed(
                            current_s1=session_counts['session1'],
                            current_s2=session_counts['session2'],
                            new_session=slot.session
                        )
                        if not allowed:
                            continue
                        
                        # Direct assignment possible
                        slot.staff_id = staff_data['staff_id']
                        slot.name = staff_data['name']
                        slot.designation = staff_data['designation']
                        slot.staff_category = staff_data['staff_category']
                        slot.dept_category = staff_data['dept_category']
                        slot.dept_name = staff_data['dept_name']
                        slot.save()
                        staff_data['remaining'] -= 1
                        unassigned_count -= 1
                        direct_assignment = True
                        print(f"   ✅ Direct assignment: {staff_data['name']}")
                        break
                    
                    if direct_assignment:
                        continue
                        
                    # SECOND: Only if direct assignment fails, try reassignment
                    for staff_data in staff_list:
                        if staff_data['session'] <= 0:
                            continue
                        
                        # Hard Constraints
                        if slot.hall_department == staff_data['dept_name']:
                            continue
                        if InvigilationSchedule.objects.filter(
                            staff_id=staff_data['staff_id'],
                            date=slot.date,
                            session=slot.session
                        ).exists():
                            continue
                        
                        # Soft Constraints
                        total_exam_days = ExamDate.objects.latest('day_no').day_no
                        if staff_data['remaining'] < total_exam_days:
                            if InvigilationSchedule.objects.filter(
                                staff_id=staff_data['staff_id'],
                                date=slot.date
                            ).exists():
                                continue
                        session_counts = InvigilationSchedule.objects.filter(
                            staff_id=staff_data['staff_id']
                        ).aggregate(
                            session1=Count(Case(When(session=1, then=1))),
                            session2=Count(Case(When(session=2, then=1)))
                        )
                        allowed, _ = is_assignment_allowed(
                            current_s1=session_counts['session1'],
                            current_s2=session_counts['session2'],
                            new_session=slot.session
                        )
                        if not allowed:
                            continue
                        
                        # Staff can take this slot - reassign them
                        slot.staff_id = staff_data['staff_id']
                        slot.name = staff_data['name']
                        slot.designation = staff_data['designation']
                        slot.staff_category = staff_data['staff_category']
                        slot.dept_category = staff_data['dept_category']
                        slot.dept_name = staff_data['dept_name']
                        slot.save()
                        
                        # Accept that their old slot becomes unassigned
                        unassigned_count -= 1
                        print(f"   ✅ Reassignment: {staff_data['name']} moved to new slot")
                        break

            # ================================================
            # PHASE 3 INSERTION POINT - END HERE
            # ================================================

        else:
            messages.warning(
                request,
                f"{dept_category}: Assigned {assigned_slots}/{total_slots} slots. "
                f"{unassigned_count} remain unassigned (due to session limits or date conflicts). "
                f"{remaining_staff} staff have remaining capacity."
                )
            
            
    return redirect('generate_schedule')  # Redirect after processing all departments


# Keep these if you still need them for other purposes
def download_assignments(request):
    if 'assignment_log' not in request.session:
        return HttpResponse("No assignment data available")
        
    df = pd.DataFrame(request.session['assignment_log'])
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Assignments', index=False)
    writer.close()
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=assignment_log.xlsx'
    return response


def download_room_data(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Room Data"

    headers = ["Hall No", "Department Category", "Department Name", "Strength", "Required Session"]
    ws.append(headers)

    rooms = Room.objects.all().values_list(
        'hall_no', 'dept_category', 'dept_name', 'strength', 'required_session'
    )
    
    for room in rooms:
        ws.append(room)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=RoomData.xlsx'
    wb.save(response)
    return response

# SAQ TEST CODE ENDS
# For printing a message
#  if remaining_slots.exists():
#                 print(f"🔍 PHASE 3: Processing {remaining_slots.count()} unassigned slots")


def download_staff_unallotted(request):
    # Create workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Staff Allotment"

    # Headers
    headers = [
        "staff_id", "name", "dept_category", "session",
        "Session 1 Allotted", "Session 2 Allotted",
        "Total Allotted", "Remaining Sessions"
    ]
    ws.append(headers)

    # Loop through all staff
    for staff in Staff.objects.all():
        # Count allotments in invigilation_schedule by staff_id + session number
        session1_allotted = InvigilationSchedule.objects.filter(staff_id=staff.staff_id, session=1).count()
        session2_allotted = InvigilationSchedule.objects.filter(staff_id=staff.staff_id, session=2).count()

        total_allotted = session1_allotted + session2_allotted
        remaining = (staff.session or 0) - total_allotted   # avoid NoneType issue

        ws.append([
            staff.staff_id,
            staff.name,
            staff.dept_category,
            staff.session,
            session1_allotted,
            session2_allotted,
            total_allotted,
            remaining
        ])

    # Return Excel file
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="staff_allotment.xlsx"'
    wb.save(response)

    return response