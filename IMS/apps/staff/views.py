import pandas as pd
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from .models import Staff, Department, Designation
from .forms import StaffUploadForm

# Set up logging
logger = logging.getLogger(__name__)


def staff_management(request):
    # Initialize queryset
    staff_list = Staff.objects.all().select_related('designation')
    
    # Handle AJAX requests differently
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
            'request': request,  # Pass request to template
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
    departments = Staff.objects.values_list('dept_name', flat=True).distinct()
    
    # File upload handling
    if request.method == 'POST':
        form = StaffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    excel_file = request.FILES['excel_file']
                    df = pd.read_excel(excel_file)
                    logger.debug(f"Columns detected: {list(df.columns)}")
                    
                    # Convert date columns safely
                    date_cols = [col for col in df.columns if 'date' in col.lower()]
                    for col in date_cols:
                        try:
                            if pd.api.types.is_datetime64_any_dtype(df[col]):
                                df[col] = df[col].apply(
                                    lambda x: x.strftime('%Y-%m-%d') if not pd.isna(x) else None
                                )
                                logger.debug(f"Converted date column: {col}")
                        except Exception as e:
                            logger.error(f"Date conversion failed for {col}: {str(e)}")
                            raise ValueError(f"Invalid date format in column '{col}'. Use YYYY-MM-DD format.")

                    required_columns = ['staff_id', 'name', 'staff_category', 'designation']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        logger.error(f"Missing columns: {missing_columns}")
                        messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                        return redirect('staff:staff-management')
                    
                    # DEBUG: Log first 3 rows
                    logger.debug(f"Sample data:\n{df.head(3).to_dict()}")

                    success_count = 0
                    for index, row in df.iterrows():
                        try:
                            # DEBUG: Log current row
                            logger.debug(f"Processing row {index+1}: {row.to_dict()}")
                            
                            designation_name = str(row['designation']).strip()
                            if not designation_name:
                                logger.warning(f"Skipping row {index+1}: Empty designation")
                                continue
                            
                            # Handle designation
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
                                logger.debug(f"Created new designation: {designation_name}")

                            # Handle date_of_joining safely
                            date_of_joining = None
                            if 'date_of_joining' in row:
                                if pd.notna(row['date_of_joining']):
                                    if isinstance(row['date_of_joining'], str):
                                        date_of_joining = row['date_of_joining']  # Already converted
                                    else:
                                        date_of_joining = row['date_of_joining'].strftime('%Y-%m-%d')

                            # Create/update staff
                            staff, created = Staff.objects.update_or_create(
                                staff_id=str(row['staff_id']).strip(),
                                defaults={
                                    'name': str(row['name']).strip(),
                                    'dept_category': str(row.get('dept_category', 'AIDED')).strip(),
                                    'designation': designation,
                                    'staff_category': str(row['staff_category']).strip(),
                                    'dept_name': str(row.get('dept_name', '')).strip(),
                                    'mobile': str(row.get('mobile', '')).strip().replace(' ', '').replace('-', '')[:17],
                                    'email': str(row.get('email', '')).strip(),
                                    'date_of_joining': date_of_joining,
                                    'is_active': bool(row.get('is_active', True))
                                }
                            )
                            success_count += 1
                            if created:
                                logger.debug(f"Created new staff: {staff.staff_id}")
                            else:
                                logger.debug(f"Updated staff: {staff.staff_id}")

                        except Exception as e:
                            logger.error(f"Failed processing row {index+1}: {str(e)}\nRow data: {row.to_dict()}")
                            raise  # Re-raise to trigger transaction rollback

                    messages.success(request, f'Successfully processed {success_count}/{len(df)} records!')
                    logger.info(f"File processed successfully. Records: {success_count}/{len(df)}")
                    return redirect('staff:staff-management')

            except Exception as e:
                logger.exception("Fatal error during file processing:")
                messages.error(request, f'Error: {str(e)} [Check server logs for details]')
        else:
            logger.error(f"Invalid form: {form.errors}")
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
        'departments': departments,
        'total_count': paginator.count,
        'page_number': page_number or 1,
        'num_pages': paginator.num_pages,
        'request': request,  # Pass request to template
    })