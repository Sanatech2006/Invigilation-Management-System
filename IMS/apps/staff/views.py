import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StaffExcelUploadForm
from .models import Staff, Department, Designation

def staff_management(request):
    if request.method == 'POST':
        form = StaffExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Read Excel file
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)
                
                # Standardize column names (case insensitive)
                df.columns = df.columns.str.strip().str.upper()
                
                # Process each row
                for _, row in df.iterrows():
                    # Get or create department
                    dept, _ = Department.objects.get_or_create(
                        dept_type=row.get('DEPTTYPE', '').strip().upper(),
                        name=row.get('DEPTNAME', '').strip()
                    )
                    
                    # Get or create designation
                    designation, _ = Designation.objects.get_or_create(
                        name=row.get('DESIGNATION', '').strip(),
                        category=row.get('CATEGORY', '').strip().upper()
                    )
                    
                    # Create staff record
                    Staff.objects.update_or_create(
                        staff_id=row['STAFF ID'].strip(),
                        defaults={
                            'name': row.get('STAFFNAME', '').strip(),
                            'category': row.get('CATEGORY', '').strip().upper(),
                            'designation': designation,
                            'department': dept,
                            'mobile': row.get('MOBNUM', '').strip(),
                            'email': row.get('MAILID', '').strip().lower(),
                            'date_of_joining': row.get('DOA', None)
                        }
                    )
                
                messages.success(request, 'Staff data imported successfully!')
                return redirect('staff_management')
            
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = StaffExcelUploadForm()
    
    staff_list = Staff.objects.all().select_related('designation', 'department')
    return render(request, 'staff/management.html', {
        'form': form,
        'staff_list': staff_list
    })