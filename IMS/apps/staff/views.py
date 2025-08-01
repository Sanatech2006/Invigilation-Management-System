import pandas as pd
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from .models import Staff, Department, Designation
from .forms import StaffUploadForm
from django.db.models.functions import Trim

# Set up logging
logger = logging.getLogger(__name__)

def staff_management(request):
    # Initialize form and queryset
    form = StaffUploadForm()
    staff_list = Staff.objects.all().select_related('designation')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    staff_category_filter = request.GET.get('staff_category')
    dept_category_filter = request.GET.get('dept_category')
    designation_filter = request.GET.get('designation')
    department_filter = request.GET.get('department')
    per_page = int(request.GET.get('per_page', 100))  # Default to 100 items per page
    
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
        staff_list = staff_list.filter(designation__name=designation_filter)
    
    if department_filter:
        staff_list = staff_list.filter(dept_name=department_filter)
    
    # Pagination
    paginator = Paginator(staff_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # For AJAX requests, return only the table HTML
    if is_ajax:
        return render(request, 'staff/staff_table.html', {
            'staff_list': page_obj,
            'request': request,
            'total_count': paginator.count,
            'page_number': page_number,
            'num_pages': paginator.num_pages,
        })
    
    # Get filter options for dropdowns
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
    departments = Staff.objects.annotate(trimmed_dept=Trim('dept_name')) \
                         .values_list('trimmed_dept', flat=True) \
                         .distinct() \
                         .order_by('trimmed_dept')
    
    # File upload handling
    if request.method == 'POST':
     form = StaffUploadForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            with transaction.atomic():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)
                
                # Debug: Show raw column names
                logger.debug(f"Original columns: {list(df.columns)}")
                
                # Normalize column names
                df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
                logger.debug(f"Normalized columns: {list(df.columns)}")
                
                # Verify required columns
                required_columns = ['staff_id', 'name', 'staff_category', 'designation',
                                  'dept_category', 'dept_name', 'mobile', 'email',
                                  'date_of_joining', 'session', 'fixed_session']
                
                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    messages.error(request, f'Missing columns: {", ".join(missing)}')
                    return redirect('staff:staff-management')

                success_count = 0
                for index, row in df.iterrows():
                    try:
                        # Debug raw values
                        raw_session = row.get('session')
                        raw_fixed = row.get('fixed_session')
                        logger.debug(f"Row {index+1} - Raw session: {raw_session}, Raw fixed: {raw_fixed}")
                        
                        # Convert session values (handles negatives)
                        def convert_value(val):
                            try:
                                if pd.isna(val) or str(val).strip() == '':
                                    return 0
                                return int(float(str(val).strip()))
                            except (ValueError, TypeError):
                                return 0
                        
                        session_val = convert_value(raw_session)
                        fixed_val = convert_value(raw_fixed)
                        
                        # Debug converted values
                        logger.debug(f"Row {index+1} - Converted session: {session_val}, Fixed: {fixed_val}")
                        
                        # Get/create designation
                        designation_name = str(row['designation']).strip()
                        designation, _ = Designation.objects.get_or_create(
                            name=designation_name,
                            defaults={'category': str(row.get('dept_category', 'Teaching')).strip()}
                        )
                        
                        # Update staff record
                        Staff.objects.update_or_create(
                            staff_id=str(row['staff_id']).strip(),
                            defaults={
                                # ... [other fields] ...
                                'session': session_val,
                                'fixed_session': fixed_val
                            }
                        )
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"Row {index+1} error: {str(e)}")
                        continue
                
                messages.success(request, f'Successfully processed {success_count}/{len(df)} records!')
                return redirect('staff:staff-management')
        
        except Exception as e:
            logger.exception("File processing failed")
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'staff/management.html', {
        'form': form,
        'staff_list': page_obj,
        'search_query': search_query,
        'messages': messages.get_messages(request),
        'staff_types': staff_types,
        'dept_categories': dept_categories,
        'departments': departments,
        'total_count': paginator.count,
        'page_number': page_number or 1,
        'num_pages': paginator.num_pages,
        'request': request,
    })