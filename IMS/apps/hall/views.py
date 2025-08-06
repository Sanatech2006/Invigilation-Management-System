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
                    
                    Room.objects.update_or_create(
                        hall_no=hall_no,
                        defaults={
                            'dept_category': str(row.get('dept_category', '')),
                            'dept_name': str(row.get('dept_name', '')),
                            'strength': strength,
                            'days': int(row.get('days', 0)),
                            'staff_required': staff_required,  # New field
                            'required_session': required_session,
                            'block': "-",
                            'staff_allotted': "Not Allotted",
                            'benches': 0,
                        }
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
    # if request.method == "POST":
        # print("this is the route")
        # halls = Room.objects.all().values() 
        # dates=ExamDate.objects.all()
        # print("dates",dates)

        # # Assuming you already have dates and halls loaded

        # for date in dates:
        #     for hall in halls:
        #         total = hall['staff_required'] * 2
        #         for i in range(total):
        #             session_number = "1" if i < total // 2 else "2"
        #             # print("gsfd",date.date)

        #             InvigilationSchedule.objects.create(
        #                 date=date.date,
        #                 session=session_number,
        #                 hall_no=hall['hall_no'],
        #                 hall_department=hall['dept_name'],
        #                 hall_dept_category=hall['dept_category'],
        #                 #set later
        #                 staff_id=None,
        #                 name=None,
        #                 designation=None,
        #                 staff_category=None,
        #                 double_session=False
                    # )
                    # print("gsfd",date.date)






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
        "Join Date"
        "Fixed session"
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



# def assign_staff(request):
#     if request.method == 'POST':
#         # Your logic here
#         print("Staff assigned")
#         # return HttpResponse("Staff assigned")
#         # Maybe redirect somewhere
#         return redirect('generate_schedule')
#     return render(request, 'your_template.html')



def generate_session(request):
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



#Assign Staff Based on no COndition 

# def assign_staff(request):
#     if request.method == 'POST':
#         # Get all staff with session > 0 and active
#         eligible_staff = Staff.objects.filter(is_active=True, session__gt=0)
#         print("staffs",eligible_staff)

#         for staff in eligible_staff:
#             # Filter existing assignments for this staff
#             current_assignments = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).count()

#             remaining_assignments = staff.session - current_assignments
#             if remaining_assignments <= 0:
#                 continue

#             # Get unassigned schedule slots
#             unassigned_slots = InvigilationSchedule.objects.filter(staff_id__isnull=True)

#             # Select random slots
#             selected_slots = random.sample(
#                 list(unassigned_slots),
#                 min(remaining_assignments, unassigned_slots.count())
#             )

#             for slot in selected_slots:
#                 slot.staff_id = staff.staff_id
#                 slot.name = staff.name
#                 slot.designation = str(staff.designation)
#                 slot.staff_category = staff.staff_category
#                 slot.dept_category = staff.dept_category
#                 slot.save()

#         print("Staff assignment completed")
#         return redirect('generate_schedule')

#     # return render(request, 'your_template.html')




# import random

# this is based on Category matching  staff_depat_category === hall_dept_category

# def assign_staff(request):
#     if request.method == 'POST':
#         eligible_staff = Staff.objects.filter(is_active=True, session__gt=0)

#         # Loop through each eligible staff member
#         for staff in eligible_staff:
#             current_assignments = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).count()
#             remaining_assignments = staff.session - current_assignments
#             if remaining_assignments <= 0:
#                 continue

#             # Filter unassigned slots that match dept_category
#             matched_slots = InvigilationSchedule.objects.filter(
#                 staff_id__isnull=True,
#                 hall_dept_category=staff.dept_category
#             )

#             # Random selection of slots
#             selected_slots = random.sample(
#                 list(matched_slots),
#                 min(remaining_assignments, matched_slots.count())
#             )

#             for slot in selected_slots:
#                 slot.staff_id = staff.staff_id
#                 slot.name = staff.name
#                 slot.designation = str(staff.designation)
#                 slot.staff_category = staff.staff_category
#                 slot.dept_category = staff.dept_category
#                 slot.save()

#         print("Staff assignment with department matching complete")
#         return redirect('generate_schedule')

#     return render(request, 'your_template.html')



# this is based on Category matching  staff_depat_category === hall_dept_category &&  dept_name != hall_Department 

def assign_staff(request):
    if request.method == 'POST':
        eligible_staff = Staff.objects.filter(is_active=True, session__gt=0)

        # Loop through each eligible staff member
        for staff in eligible_staff:
            current_assignments = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).count()
            remaining_assignments = staff.session - current_assignments
            if remaining_assignments <= 0:
                continue

            # Filter unassigned slots that:
            # 1. Match the staff's dept_category
            # 2. Have a hall_department DIFFERENT from the staff's department dept_name
            matched_slots = InvigilationSchedule.objects.filter(
                staff_id__isnull=True,
                hall_dept_category=staff.dept_category
            ).exclude(
                hall_department=staff.dept_name
            )

            # Random selection of slots
            slot_count = matched_slots.count()
            if slot_count == 0:
                continue  # Skip if no eligible slots

            selected_slots = random.sample(
                list(matched_slots),
                min(remaining_assignments, slot_count)
            )

            for slot in selected_slots:
                slot.staff_id = staff.staff_id
                slot.name = staff.name
                slot.designation = str(staff.designation)
                slot.staff_category = staff.staff_category
                slot.dept_category = staff.dept_category
                slot.save()

        print("✅ Staff assignment with department conflict exclusion complete")
        return redirect('generate_schedule')

    return render(request, 'your_template.html')






# def assign_slot(slot, staff, double=False):
#     slot.staff_id = staff.staff_id
#     slot.name = staff.name
#     slot.designation = str(staff.designation)
#     slot.staff_category = staff.staff_category
#     slot.dept_category = staff.dept_category
#     slot.double_session = double
#     slot.save()

# def assign_staff(request):
#     if request.method == 'POST':
#         exam_dates = list(ExamDate.objects.all().order_by('date'))
#         total_dates = len(exam_dates)

#         eligible_staff = Staff.objects.filter(is_active=True, session__gt=0)

#         for staff in eligible_staff:
#             current_assignments = InvigilationSchedule.objects.filter(staff_id=staff.staff_id).count()
#             remaining_assignments = staff.session - current_assignments
#             if remaining_assignments <= 0:
#                 continue

#             matched_slots = InvigilationSchedule.objects.filter(
#                 staff_id__isnull=True,
#                 hall_dept_category=staff.dept_category
#             ).exclude(
#                 hall_department=staff.dept_name
#             ).order_by('date', 'session')

#             assignment_counter = 0

#             for date in exam_dates:
#                 if assignment_counter >= remaining_assignments:
#                     break

#                 slots_for_day = matched_slots.filter(date=date.date)

#                 # Group slots by hall
#                 hall_groups = defaultdict(list)
#                 for slot in slots_for_day:
#                     hall_groups[slot.hall_no].append(slot)

#                 # Find halls with remaining capacity
#                 for hall, hall_slots in hall_groups.items():
#                     while assignment_counter < remaining_assignments and hall_slots:
#                         double = assignment_counter >= total_dates  # overflow flag
#                         assign_slot(hall_slots.pop(0), staff, double)
#                         assignment_counter += 1
#                     if assignment_counter >= remaining_assignments:
#                         break

#         print("✅ Continuous + fair staff assignment complete")
#         return redirect('generate_schedule')

#     return render(request, 'your_template.html')
    