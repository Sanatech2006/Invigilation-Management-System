import pandas as pd
from django.shortcuts import render
from .models import Room
from django.db.models import Sum
from staff.logic import allocate_sessions
from django.http import HttpResponse
from openpyxl import Workbook
from apps.staff.models import Staff
from django.utils import timezone
import datetime

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
    # Calculate total sessions required by category
    categories = Room.objects.values('dept_category').annotate(
        total_sessions=Sum('required_session')
    ).order_by('dept_category')
    
    # Get staff counts with case-insensitive matching
    staff_counts = {
        'Aided': Staff.objects.filter(dept_category__iexact='aided').count(),
        'SFM': Staff.objects.filter(dept_category__iexact='sfm').count(),
        'SFW': Staff.objects.filter(dept_category__iexact='sfw').count()
    }
    
    # Format the data for display
    required_session = {
        item['dept_category']: item['total_sessions']
        for item in categories
    }
    
    # Call the allocation function (only if form submitted)
    allocation_results = None
    if request.method == 'POST' and 'allocate_sessions' in request.POST:
        allocation_results = allocate_sessions(required_session)
    
    # Format the data for display with staff counts
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
        'categories': ['Aided', 'SFM', 'SFW']
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
    ]
    ws.append(headers)
    
    # Get all staff data with correct comma separation
    staff_data = Staff.objects.all().values_list(
        'staff_id',      # Staff ID
        'name',          # Name
        'dept_name',     # Department
        'dept_category', # Department Category
        'session',       # Sessions
        'date_of_joining' # Join Date
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