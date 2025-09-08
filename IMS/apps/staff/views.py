import pandas as pd
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import transaction
from .models import  Department, Designation
from .forms import StaffUploadForm
from apps.staff.models import Staff
from django.db.models.functions import Trim
from datetime import datetime
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Set up logging
logger = logging.getLogger(__name__)

def get_staff_counts_by_dept():
    """Returns a dictionary of staff counts by department category"""
    return dict(Staff.objects.values('dept_category')
                          .annotate(count=Count('id'))
                          .values_list('dept_category', 'count'))

def staff_management(request):
    # Initialize form and queryset
    form = StaffUploadForm()
    staff_list = Staff.objects.all().select_related('designation')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return render(request, 'staff/staff_table.html', {
            'staff_list': page_obj,
            'request': request,
            'total_count': paginator.count,
            'page_number': page_number,
            'num_pages': paginator.num_pages,
            # Add filter context to maintain state
            'search_query': search_query,
            'staff_category_filter': staff_category_filter,
            'dept_category_filter': dept_category_filter,
            'designation_filter': designation_filter,
            'department_filter': department_filter,
        })
    
    # Get staff counts - moved up to ensure it's available in all contexts
    staff_counts = get_staff_counts_by_dept()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    staff_category_filter = request.GET.get('staff_category')
    dept_category_filter = request.GET.get('dept_category')
    designation_filter = request.GET.get('designation')
    department_filter = request.GET.get('department')
    per_page = int(request.GET.get('per_page', 100))
    staff_list = Staff.objects.all().select_related('designation')
    
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
    
    # Get count BEFORE pagination
    total_filtered_count = staff_list.count()
    
    # Then apply pagination
    paginator = Paginator(staff_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX response
    if is_ajax:
        return render(request, 'staff/staff_table.html', {
            'staff_list': page_obj,
            'total_count': staff_list.count(), 
            'page_number': page_number,
            'num_pages': paginator.num_pages,
            # Include filter values to maintain state
            'search_query': search_query,
            'staff_category_filter': staff_category_filter,
            'dept_category_filter': dept_category_filter,
            'designation_filter': designation_filter,
            'department_filter': department_filter,
        })
     
    # Get filter options
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
                    # Clear existing data
                    deleted_count, _ = Staff.objects.all().delete()
                    logger.info(f"Deleted {deleted_count} existing staff records")
                    
                    excel_file = request.FILES['excel_file']
                    
                    # Read Excel file with error handling
                    try:
                        df = pd.read_excel(
                            excel_file,
                            engine='openpyxl',
                            dtype=str,  # Read all columns as strings
                        )
                    except Exception as e:
                        logger.error(f"Error reading Excel file: {str(e)}")
                        messages.error(request, f"Error reading Excel file: {str(e)}")
                        return redirect('staff:staff-management')
                    
                    # Log sample data before processing
                    logger.debug(f"Raw data sample:\n{df.head(3).to_dict()}")
                    
                    # Normalize column names
                    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
                    
                    # Verify required columns
                    required_columns = [
                        'staff_id', 'name', 'staff_category', 'designation',
                        'dept_category', 'dept_name', 'mobile', 'email',
                        'date_of_joining', 'session', 'fixed_session','role'
                    ]
                    
                    missing = [col for col in required_columns if col not in df.columns]
                    if missing:
                        msg = f'Missing required columns: {", ".join(missing)}'
                        logger.error(msg)
                        messages.error(request, msg)
                        return redirect('staff:staff-management')

                    # Process records
                    success_count = 0
                    error_rows = []
                    
                    for index, row in df.iterrows():
                        row_errors = []
                        staff_id = str(row['staff_id']).strip()
                        
                        try:
    # Validate required fields
                            if not staff_id:
                                row_errors.append("Missing staff ID")
                                raise ValueError("Missing staff ID")

                            # Get/create designation
                            designation_name = str(row['designation']).strip()
                            if not designation_name:
                                row_errors.append("Missing designation")
                                raise ValueError("Missing designation")

                            designation, _ = Designation.objects.get_or_create(
                                name=designation_name,
                                defaults={'category': str(row.get('dept_category', 'Teaching')).strip()}
                            )
                            
                            # Prepare data - reading dates as strings
                            staff_data = {
                                'name': str(row['name']).strip(),
                                'staff_category': str(row['staff_category']).strip(),
                                'designation': designation,
                                'dept_category': str(row['dept_category']).strip(),
                                'dept_name': str(row['dept_name']).strip(),
                                'mobile': str(row['mobile']).strip(),
                                'email': str(row['email']).strip(),
                                'date_of_joining': str(row['date_of_joining']).strip() if pd.notna(row['date_of_joining']) else None,
                                'session': int(float(str(row['session']).strip() or -1)),
                                'fixed_session': int(float(str(row['fixed_session']).strip() or 0)),
                                'is_active': True,
                            }

                            # Safely add role field
                            role_value = row.get('role', None)
                            if role_value is not None and not pd.isna(role_value):
                                try:
                                    staff_data['role'] = int(float(role_value))
                                except (ValueError, TypeError):
                                    # Optionally log error or set default role here
                                    raise ValueError(f"Invalid role value '{role_value}' for staff_id {staff_id}")
                            else:
                                # Optional: omit role or assign default if needed
                                pass
                            
                            # Set password as staff_id (if needed)
                            staff_data['password'] = staff_id
                            
                            # Single create/update call
                            Staff.objects.update_or_create(staff_id=staff_id, defaults=staff_data)
                            success_count += 1

                        except Exception as e:
                            error_msg = f"{str(e)}: {', '.join(row_errors)}" if row_errors else str(e)
                            error_rows.append(f"Row {index+2} (ID: {staff_id}): {error_msg}")
                            logger.error(f"Error in row {index+2}: {error_msg}\n{traceback.format_exc()}")
                            continue

                    
                    # Final report
                    msg = f"Successfully processed {success_count}/{len(df)} records"
                    if error_rows:
                        msg += f" with {len(error_rows)} errors"
                        logger.error(f"Import completed with {len(error_rows)} errors")
                    
                    messages.success(request, msg)
                    logger.info(msg)
                    return redirect('staff:staff-management')
            
            except Exception as e:
                logger.exception("Critical error during staff import")
                messages.error(request, f'System error: {str(e)}')
                return redirect('staff:staff-management')
    
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

import pandas as pd
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import transaction
from .models import Staff, Department, Designation
from .forms import StaffUploadForm
from django.db.models.functions import Trim
from datetime import datetime
import traceback
from django.http import HttpResponse
import openpyxl

# Set up logging
logger = logging.getLogger(__name__)

def get_staff_counts_by_dept():
    """Returns a dictionary of staff counts by department category"""
    return dict(Staff.objects.values('dept_category')
                          .annotate(count=Count('id'))
                          .values_list('dept_category', 'count'))

def staff_management(request):
    # Initialize form and queryset
    form = StaffUploadForm()
    staff_list = Staff.objects.all().select_related('designation')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return render(request, 'staff/staff_table.html', {
            # 'staff_list': page_obj,
            'request': request,
            # 'total_count': paginator.count,
            # 'page_number': page_number,
            # 'num_pages': paginator.num_pages,
            # Add filter context to maintain state
            'search_query': search_query,
            'staff_category_filter': staff_category_filter,
            'dept_category_filter': dept_category_filter,
            'designation_filter': designation_filter,
            'department_filter': department_filter,
        })
    
    # Get staff counts - moved up to ensure it's available in all contexts
    staff_counts = get_staff_counts_by_dept()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    staff_category_filter = request.GET.get('staff_category')
    dept_category_filter = request.GET.get('dept_category')
    designation_filter = request.GET.get('designation')
    department_filter = request.GET.get('department')
    per_page = int(request.GET.get('per_page', 100))
    staff_list = Staff.objects.all().select_related('designation')
    
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
    
    # Get count BEFORE pagination
    total_filtered_count = staff_list.count()
    
    # Then apply pagination
    # paginator = Paginator(staff_list, per_page)
    # page_number = request.GET.get('page', 1)
    # page_obj = paginator.get_page(page_number)

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'staff/staff_table.html', {
            'staff_list': staff_list,  # pass full queryset now
            'total_count': total_filtered_count,
            'search_query': search_query,
            'staff_category_filter': staff_category_filter,
            'dept_category_filter': dept_category_filter,
            'designation_filter': designation_filter,
            'department_filter': department_filter,
        })
     
    # Get filter options
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
                    # Clear existing data
                    deleted_count, _ = Staff.objects.all().delete()
                    logger.info(f"Deleted {deleted_count} existing staff records")
                    
                    excel_file = request.FILES['excel_file']
                    
                    # Read Excel file with error handling
                    try:
                        df = pd.read_excel(
                            excel_file,
                            engine='openpyxl',
                            dtype=str,  # Read all columns as strings
                        )
                    except Exception as e:
                        logger.error(f"Error reading Excel file: {str(e)}")
                        messages.error(request, f"Error reading Excel file: {str(e)}")
                        return redirect('staff:staff-management')
                    
                    # Log sample data before processing
                    logger.debug(f"Raw data sample:\n{df.head(3).to_dict()}")
                    
                    # Normalize column names
                    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
                    
                    # Verify required columns
                    required_columns = [
                        'staff_id', 'name', 'staff_category', 'designation',
                        'dept_category', 'dept_name', 'mobile', 'email',
                        'date_of_joining', 'session', 'fixed_session','role'
                    ]
                    
                    missing = [col for col in required_columns if col not in df.columns]
                    if missing:
                        msg = f'Missing required columns: {", ".join(missing)}'
                        logger.error(msg)
                        messages.error(request, msg)
                        return redirect('staff:staff-management')

                    # Process records
                    success_count = 0
                    error_rows = []
                    
                    for index, row in df.iterrows():
                        row_errors = []
                        staff_id = str(row['staff_id']).strip()
                        try:
                            existing_staff = Staff.objects.get(staff_id=staff_id)
                            existing_password = existing_staff.password
                        except Staff.DoesNotExist:
                            existing_password = None

                        password_to_use = existing_password if existing_password is not None else staff_id

                        try:
                            # Validate required fields
                            if not staff_id:
                                row_errors.append("Missing staff ID")
                                raise ValueError("Missing staff ID")
                            
                            # Get/create designation
                            designation_name = str(row['designation']).strip()
                            if not designation_name:
                                row_errors.append("Missing designation")
                                raise ValueError("Missing designation")
                            
                            designation, _ = Designation.objects.get_or_create(
                                name=designation_name,
                                defaults={'category': str(row.get('dept_category', 'Teaching')).strip()}
                            )

                            password_to_use = existing_password if existing_password is not None else staff_id                   
                            # Prepare data - reading dates as strings
                            staff_data = {
                                'name': str(row['name']).strip(),
                                'staff_category': str(row['staff_category']).strip(),
                                'designation': designation,
                                'dept_category': str(row['dept_category']).strip(),
                                'dept_name': str(row['dept_name']).strip(),
                                'mobile': str(row['mobile']).strip(),
                                'email': str(row['email']).strip(),
                                'date_of_joining': str(row['date_of_joining']).strip() if pd.notna(row['date_of_joining']) else None,
                                'session': int(float(str(row['session']).strip() or -1)),
                                'fixed_session': int(float(str(row['fixed_session']).strip() or 0)),
                                'is_active': True,
                                'password': password_to_use,
                            }

                            Staff.objects.update_or_create(staff_id=staff_id, defaults=staff_data)
                            role_value = row.get('role', None)
                            if role_value is not None and not pd.isna(role_value):
                                try:
                                    staff_data['role'] = int(float(role_value))
                                except (ValueError, TypeError) as e:
                                    raise ValueError(f"Invalid role value '{role_value}' for staff_id {staff_id}: {str(e)}")
                            else:
                                # If no role provided, optional: skip or set default here
                                pass
                            
                            # Create/update record
                            Staff.objects.update_or_create(
                                staff_id=staff_id,
                                defaults=staff_data
                            )
                            success_count += 1
                            
                        except Exception as e:
                            error_msg = f"{str(e)}: {', '.join(row_errors)}" if row_errors else str(e)
                            error_rows.append(f"Row {index+2} (ID: {staff_id}): {error_msg}")
                            logger.error(f"Error in row {index+2}: {error_msg}\n{traceback.format_exc()}")
                            continue
                    
                    # Final report
                    msg = f"Successfully processed {success_count}/{len(df)} records"
                    if error_rows:
                        msg += f" with {len(error_rows)} errors"
                        logger.error(f"Import completed with {len(error_rows)} errors")
                    
                    messages.success(request, msg)
                    logger.info(msg)
                    return redirect('staff:staff-management')
            
            except Exception as e:
                logger.exception("Critical error during staff import")
                messages.error(request, f'System error: {str(e)}')
                return redirect('staff:staff-management')
    
    return render(request, 'staff/management.html', {
        'form': form,
        'staff_list': staff_list,  # pass full queryset here also
        'search_query': search_query,
        'messages': messages.get_messages(request),
        'staff_types': staff_types,
        'dept_categories': dept_categories,
        'departments': departments,
        'total_count': total_filtered_count,
        'request': request,
    })

def download_staff_data(request):
    # Create a workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Staff Data"

    # Header row
    headers = ["Staff ID", "Name", "Staff Type", "Designation", "Dept Category", "Dept Name","Role", "Mobile" ]
    ws.append(headers)

    # Fetch staff records
    staff_qs = Staff.objects.all().values_list(
        "staff_id", "name", "staff_category", "designation", "dept_category", "dept_name","role", "mobile"
    )

    for row in staff_qs:
        ws.append(row)

    # Prepare HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=staff_data.xlsx'
    wb.save(response)
    return response

@csrf_exempt
def add_staff(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Malformed JSON.'})
            staff_id = data.get('staff_id')
            name = data.get('name')
            staff_category = data.get('staff_category')
            designation_name = data.get('designation')  # get name here
            dept_category = data.get('dept_category')
            dept_name = data.get('dept_name')
            mobile = data.get('mobile')
            email = data.get('email')
            date_joining = data.get('date_of_joining')
            role = data.get('role')
            fixed_session = data.get('fixed_session')
        else:
            staff_id = request.POST.get('staff_id')
            name = request.POST.get('name')
            staff_category = request.POST.get('staff_category')
            designation_name = request.POST.get('designation')
            dept_category = request.POST.get('dept_category')
            dept_name = request.POST.get('dept_name')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            date_joining = request.POST.get('date_of_joining')
            role = request.POST.get('role')
            fixed_session = request.POST.get('fixed_session')

        if not all([staff_id, name, dept_name]):
            return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'})

        if Staff.objects.filter(staff_id=staff_id).exists():
            return JsonResponse({'success': False, 'error': 'Staff ID already exists'})

        # Lookup or create Designation object
        designation = None
        if designation_name:
            designation, _ = Designation.objects.get_or_create(name=designation_name)

        date_of_joining = data.get('date_of_joining')

        if date_of_joining:
            try:
                date_of_joining = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date format'})

        try:
            role = int(role) if role else 0
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid numeric value for role'})

        try:
            Staff.objects.create(
                staff_id=staff_id,
                name=name,
                staff_category=staff_category,
                designation=designation,
                dept_category=dept_category,
                dept_name=dept_name,
                mobile=mobile,
                email=email,
                date_of_joining=date_of_joining,
                role=role,
                fixed_session=fixed_session,
                is_active=True
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    
def search_staff(request):
    q = request.GET.get('q', '')
    staffs = Staff.objects.filter(
        Q(staff_id__icontains=q) | Q(name__icontains=q)
    ).values('staff_id', 'name')[:20]

    results = [
        {"id": staff['staff_id'], "text": f"{staff['staff_id']} – {staff['name']}"}
        for staff in staffs
    ]
    return JsonResponse({"results": results})

#edit staff

def get_staff_details(request):
    staff_id = request.GET.get('staff_id', '').strip()
    if not staff_id:
        return JsonResponse({'success': False, 'error': 'Missing staff_id'})

    try:
        staff = Staff.objects.get(staff_id=staff_id)

        # Safe date formatting handling
        doj = staff.date_of_joining
        if isinstance(doj, str):
            date_of_joining = doj  # already string, no formatting needed
        elif hasattr(doj, 'strftime'):
            date_of_joining = doj.strftime('%Y-%m-%d')
        else:
            date_of_joining = ''

        data = {
            'name': staff.name or '',
            'staff_category': staff.staff_category or '',
            'designation': getattr(staff.designation, 'name', '') if staff.designation else '',
            'dept_category': staff.dept_category or '',
            'dept_name': staff.dept_name or '',
            'mobile': staff.mobile or '',
            'email': staff.email or '',
            'date_of_joining': date_of_joining,
            'role': staff.role if staff.role is not None else '',
            'fixed_session': staff.fixed_session if staff.fixed_session is not None else '',
            'session': staff.session if staff.session is not None else '',
        }

        return JsonResponse({'success': True, 'staff': data})

    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Staff not found'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def test_api(request):
    return JsonResponse({'status': 'ok'})


@csrf_exempt  # Or handle CSRF properly with middleware and token header from JS
def update_staff(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid HTTP method'})

    try:
        data = json.loads(request.body)
        staff_id = data.get('staff_id')
        staff = Staff.objects.get(staff_id=staff_id)

        staff.name = data.get('name', staff.name)
        staff.staff_category = data.get('staff_category', staff.staff_category)

        designation_name = data.get('designation')
        if designation_name:
            try:
                designation_obj = Designation.objects.get(name=designation_name)
                staff.designation = designation_obj
            except Designation.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'Designation "{designation_name}" not found.'})

        staff.dept_category = data.get('dept_category', staff.dept_category)
        staff.dept_name = data.get('dept_name', staff.dept_name)
        staff.mobile = data.get('mobile', staff.mobile)
        staff.email = data.get('email', staff.email)
        staff.date_of_joining = data.get('date_of_joining', staff.date_of_joining)
        staff.role = data.get('role', staff.role)
        staff.fixed_session = data.get('fixed_session', staff.fixed_session)
        staff.session = data.get('session', staff.session)
        staff.save()
        return JsonResponse({'success': True})

    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Staff not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

#delete staff

@csrf_exempt  # Use with CSRF token in headers as above or adjust accordingly
def delete_staff(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        data = json.loads(request.body)
        staff_id = data.get('staff_id')
        if not staff_id:
            return JsonResponse({'success': False, 'error': 'No staff_id provided'})

        staff = Staff.objects.get(staff_id=staff_id)
        staff.delete()
        return JsonResponse({'success': True})
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Staff not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})