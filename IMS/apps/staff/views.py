import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Staff, Department, Designation
from .forms import StaffUploadForm


def staff_management(request):
    # Initialize queryset
    staff_list = Staff.objects.all().select_related('designation')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    staff_category_filter = request.GET.get('staff_category')
    dept_category_filter = request.GET.get('dept_category')
    designation_filter = request.GET.get('designation')
    department_filter = request.GET.get('department')
    
    # Apply filters
    if search_query:
        staff_list = staff_list.filter(
            Q(staff_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(dept_name__icontains=search_query) |
            Q(designation__name__icontains=search_query)
        )
    
    if staff_category_filter:
        staff_list = staff_list.filter(staff_category=staff_category_filter)
    
    if dept_category_filter:
        staff_list = staff_list.filter(dept_category=dept_category_filter)
    
    if designation_filter:
        staff_list = staff_list.filter(designation__id=designation_filter)
    
    if department_filter:
        staff_list = staff_list.filter(dept_name=department_filter)
    
    # Pagination
    paginator = Paginator(staff_list, 70)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter options
    staff_types = Staff.objects.exclude(staff_category__isnull=True)\
                              .exclude(staff_category__exact='')\
                              .order_by('staff_category')\
                              .values_list('staff_category', flat=True)\
                              .distinct()
    dept_categories = Staff.objects.exclude(dept_category__isnull=True)\
                              .exclude(dept_category__exact='')\
                              .order_by('dept_category')\
                              .values_list('dept_category', flat=True)\
                              .distinct()
    designations = Designation.objects.all().order_by('name')
    departments = Staff.objects.values_list('dept_name', flat=True).distinct()
    
    # File upload handling
    if request.method == 'POST':
        form = StaffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)
                
                required_columns = ['staff_id', 'name', 'staff_category', 'designation']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                    return redirect('staff:staff-management')
                
                for index, row in df.iterrows():
                    designation_name = str(row['designation']).strip()
                    if not designation_name:
                        continue  
                        
                    try:
                        designation = Designation.objects.get(name=designation_name)
                        if 'dept_category' in row and pd.notna(row['dept_category']):
                            designation.category = str(row['dept_category']).strip()
                            designation.save()
                    except Designation.DoesNotExist:
                        designation = Designation.objects.create(
                            name=designation_name,
                            category=str(row.get('dept_category', 'Teaching')).strip()
                        )
                    
                    Staff.objects.update_or_create(
                        staff_id=str(row['staff_id']).strip(),
                        defaults={
                            'name': str(row['name']).strip(),
                            'dept_category': str(row.get('dept_category', 'AIDED')).strip(),
                            'designation': designation,
                            'staff_category': str(row['staff_category']).strip(),  
                            'dept_name': str(row.get('dept_name', '')).strip(),  
                            'mobile': str(row.get('mobile', '')).strip().replace(' ', '').replace('-', '')[:17],
                            'email': str(row.get('email', '')).strip(),
                            'date_of_joining': row.get('date_of_joining'),
                            'is_active': bool(row.get('is_active', True))
                        }
                    )
                
                messages.success(request, f'Successfully imported {len(df)} staff records!')
                return redirect('staff:staff-management') 
            
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            messages.error(request, 'Invalid file format. Please upload an Excel file (.xlsx, .xls)')
    else:
        form = StaffUploadForm()
    
    return render(request, 'staff/management.html', {
        'form': form,
        'staff_list': page_obj,
        'search_query': search_query,
        'messages': messages.get_messages(request),
        'staff_types': staff_types,
        'dept_categories': dept_categories,
        'designations': designations,
        'departments': departments,
        'current_staff_category': staff_category_filter,
        'current_dept_category': dept_category_filter,
        'current_designation': designation_filter,
        'current_department': department_filter
    })