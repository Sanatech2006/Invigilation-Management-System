import openpyxl
import pandas as pd
import logging
import re
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
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json


# Set up logging
logger = logging.getLogger(__name__)

def get_staff_counts_by_dept():
    """Returns a dictionary of staff counts by department category"""
    return dict(Staff.objects.values('dept_category')
                          .annotate(count=Count('id'))
                          .values_list('dept_category', 'count'))

def clean_date_str(val):
    """Safely format date values into YYYY-MM-DD or return clean string."""
    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'none', 'nat'):
        return None
    if ' ' in s:
        s = s.split(' ')[0]
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return s

def clean_mobile_str(val):
    """Normalize mobile phone number string."""
    if val is None or pd.isna(val):
        return ''
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    cleaned = ''.join(c for i, c in enumerate(s) if c.isdigit() or (i == 0 and c == '+'))
    return cleaned

def clean_email_str(val):
    """
    Clean email string: handles multiple emails (takes the first/primary),
    removes errant internal spaces or line breaks, and returns cleaned email string.
    """
    if val is None or pd.isna(val):
        return ''
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'none', 'null', 'na', 'n/a'):
        return ''
    # If multiple emails separated by comma, semicolon, or newline, take the primary (first)
    first = re.split(r'[,;\n]+', s)[0].strip()
    # Remove errant spaces inside email e.g. "Smohamed Anas777@gmail.com" or "user@gmail. com"
    cleaned = re.sub(r'\s+', '', first)
    return cleaned

def is_valid_email_str(val):
    """Validate email address format."""
    if not val:
        return False
    try:
        validate_email(val)
        return True
    except ValidationError:
        return False


def parse_and_validate_staff_excel(df):
    """
    Parses a pandas DataFrame of staff records and performs comprehensive validation,
    in-file duplicate detection, and database matching.
    """
    # Normalize headers
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

    required_columns = [
        'staff_id', 'name', 'staff_category', 'designation',
        'dept_category', 'dept_name', 'mobile', 'email',
        'date_of_joining', 'session', 'fixed_session', 'role'
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return {
            'valid_format': False,
            'missing_columns': missing,
            'summary': None,
            'records': [],
            'to_create': [],
            'to_update': [],
            'excel_staff_ids': set(),
            'error_rows': [],
        }

    existing_staff_dict = {s.staff_id: s for s in Staff.objects.all()}

    records = []
    to_create = []
    to_update = []
    error_rows = []
    seen_staff_ids = {}  # staff_id -> {'row': excel_row, 'name': name}
    excel_staff_ids = set()

    total_data_rows = 0
    insert_count = 0
    update_count = 0
    duplicate_count = 0
    error_count = 0

    for index, row in df.iterrows():
        excel_row = index + 2

        raw_staff_id = row.get('staff_id', '')
        staff_id = str(raw_staff_id).strip() if pd.notna(raw_staff_id) else ''

        raw_name = row.get('name', '')
        name = str(raw_name).strip() if pd.notna(raw_name) else ''

        # Completely empty rows (e.g. at end of file) are skipped silently
        if (not staff_id or staff_id.lower() == 'nan') and (not name or name.lower() == 'nan'):
            continue

        total_data_rows += 1
        row_errors = []

        # ── 1. Staff ID ──
        if not staff_id or staff_id.lower() == 'nan':
            row_errors.append('Staff ID is required.')

        # ── 2. Name ──
        if not name or name.lower() == 'nan':
            row_errors.append('Staff name is required.')

        # ── 3. Staff Category ──
        raw_staff_cat = row.get('staff_category', '')
        staff_category = str(raw_staff_cat).strip() if pd.notna(raw_staff_cat) else ''
        if not staff_category or staff_category.lower() == 'nan':
            row_errors.append('Staff category is required.')

        # ── 4. Designation ──
        raw_desig = row.get('designation', '')
        designation_name = str(raw_desig).strip() if pd.notna(raw_desig) else ''
        if not designation_name or designation_name.lower() == 'nan':
            row_errors.append('Designation is required.')

        # ── 5. Dept Category ──
        raw_dept_cat = row.get('dept_category', '')
        dept_category = str(raw_dept_cat).strip() if pd.notna(raw_dept_cat) else ''
        if not dept_category or dept_category.lower() == 'nan':
            row_errors.append('Department category is required.')

        # ── 6. Dept Name ──
        raw_dept_name = row.get('dept_name', '')
        dept_name = str(raw_dept_name).strip() if pd.notna(raw_dept_name) else ''
        if not dept_name or dept_name.lower() == 'nan':
            row_errors.append('Department name is required.')

        # ── 7. Mobile ──
        raw_mobile = row.get('mobile', '')
        mobile = clean_mobile_str(raw_mobile)
        if not mobile:
            row_errors.append('Mobile number is required.')
        elif len(mobile) < 7:
            row_errors.append(f'Invalid mobile number: "{raw_mobile}".')

        # ── 8. Email ──
        raw_email = row.get('email', '')
        email = clean_email_str(raw_email)
        if not email:
            row_errors.append('Email address is required.')
        elif not is_valid_email_str(email):
            row_errors.append(f'Invalid email address: "{raw_email}".')

        # ── 9. Date of Joining ──
        raw_doj = row.get('date_of_joining', '')
        doj = clean_date_str(raw_doj)

        # ── 10. Session ──
        raw_session = row.get('session', '')
        session_val = None
        try:
            session_str = str(raw_session).strip()
            if not session_str or session_str.lower() in ('nan', 'none'):
                session_val = -1
            else:
                session_val = int(float(session_str))
        except (ValueError, TypeError):
            row_errors.append(f'Session must be a whole number, got "{raw_session}".')

        # ── 11. Fixed Session ──
        raw_fixed = row.get('fixed_session', '')
        fixed_session_val = None
        try:
            fixed_str = str(raw_fixed).strip()
            if not fixed_str or fixed_str.lower() in ('nan', 'none'):
                fixed_session_val = 0
            else:
                fixed_session_val = int(float(fixed_str))
        except (ValueError, TypeError):
            row_errors.append(f'Fixed session must be a whole number, got "{raw_fixed}".')

        # ── 12. Role ──
        raw_role = row.get('role', None)
        parsed_role = 4  # default to Staff (4)
        if raw_role is not None and not pd.isna(raw_role):
            try:
                role_str = str(raw_role).strip()
                if role_str and role_str.lower() not in ('nan', 'none'):
                    parsed_role = int(float(role_str))
            except (ValueError, TypeError):
                row_errors.append(f'Role must be a whole number, got "{raw_role}".')

        # If any validation errors on this row:
        if row_errors:
            error_count += 1
            for err in row_errors:
                error_rows.append({
                    'row': excel_row,
                    'staff_id': staff_id,
                    'field': 'validation',
                    'value': '',
                    'message': err,
                })
            err_msg = '; '.join(row_errors)
            records.append({
                'row': excel_row,
                'row_number': excel_row,
                'staff_id': staff_id or '—',
                'name': name or '—',
                'staff_category': staff_category or '—',
                'designation': designation_name or '—',
                'dept_category': dept_category or '—',
                'dept_name': dept_name or '—',
                'mobile': mobile or '—',
                'email': email or '—',
                'date_of_joining': doj or '—',
                'session': session_val if session_val is not None else '—',
                'fixed_session': fixed_session_val if fixed_session_val is not None else '—',
                'role': parsed_role if parsed_role is not None else '—',
                'action': 'ERROR',
                'status': 'error',
                'status_label': 'Error',
                'message': err_msg,
                'status_note': err_msg,
                'errors': row_errors,
            })
            continue

        # In-file duplicate check:
        if staff_id in seen_staff_ids:
            duplicate_count += 1
            first_seen = seen_staff_ids[staff_id]
            note = f'Duplicate Staff ID (First defined at Row {first_seen["row"]} for {first_seen["name"]}) — Skipped'
            records.append({
                'row': excel_row,
                'row_number': excel_row,
                'staff_id': staff_id,
                'name': name,
                'staff_category': staff_category,
                'designation': designation_name,
                'dept_category': dept_category,
                'dept_name': dept_name,
                'mobile': mobile,
                'email': email,
                'date_of_joining': doj or '',
                'session': session_val,
                'fixed_session': fixed_session_val,
                'role': parsed_role,
                'action': 'DUPLICATE',
                'status': 'duplicate',
                'status_label': 'Duplicate (Skipped)',
                'message': note,
                'status_note': note,
                'errors': [],
            })
            continue

        # Valid, unique in file:
        seen_staff_ids[staff_id] = {'row': excel_row, 'name': name}
        excel_staff_ids.add(staff_id)

        existing_staff = existing_staff_dict.get(staff_id)
        if existing_staff:
            update_count += 1
            action = 'update'
            action_code = 'UPDATE'
            status_label = 'Update'
            status_note = 'Existing record will be updated in database'
            to_update.append({
                'id': existing_staff.id,
                'staff_id': staff_id,
                'name': name,
                'staff_category': staff_category,
                'designation_name': designation_name,
                'dept_category': dept_category,
                'dept_name': dept_name,
                'mobile': mobile,
                'email': email,
                'date_of_joining': doj,
                'session': session_val,
                'fixed_session': fixed_session_val,
                'role': parsed_role,
                'password': existing_staff.password or staff_id,
            })
        else:
            insert_count += 1
            action = 'insert'
            action_code = 'INSERT'
            status_label = 'New'
            status_note = 'New staff record will be inserted into database'
            to_create.append({
                'staff_id': staff_id,
                'name': name,
                'staff_category': staff_category,
                'designation_name': designation_name,
                'dept_category': dept_category,
                'dept_name': dept_name,
                'mobile': mobile,
                'email': email,
                'date_of_joining': doj,
                'session': session_val,
                'fixed_session': fixed_session_val,
                'role': parsed_role,
                'password': staff_id,
            })

        records.append({
            'row': excel_row,
            'row_number': excel_row,
            'staff_id': staff_id,
            'name': name,
            'staff_category': staff_category,
            'designation': designation_name,
            'dept_category': dept_category,
            'dept_name': dept_name,
            'mobile': mobile,
            'email': email,
            'date_of_joining': doj or '',
            'session': session_val,
            'fixed_session': fixed_session_val,
            'role': parsed_role,
            'action': action_code,
            'status': action,
            'status_label': status_label,
            'message': status_note,
            'status_note': status_note,
            'errors': [],
        })

    ready_to_store = insert_count + update_count
    successfully_processed = total_data_rows

    summary = {
        'total_rows': total_data_rows,
        'successfully_processed': successfully_processed,
        'ready_to_store': ready_to_store,
        'to_create': insert_count,
        'to_update': update_count,
        'to_insert_count': insert_count,
        'to_update_count': update_count,
        'duplicate_count': duplicate_count,
        'error_count': error_count,
    }

    return {
        'valid_format': True,
        'missing_columns': [],
        'summary': summary,
        'records': records,
        'to_create': to_create,
        'to_update': to_update,
        'excel_staff_ids': excel_staff_ids,
        'error_rows': error_rows,
    }

def apply_staff_import(to_create, to_update, excel_staff_ids):
    """
    Executes database bulk insert/update and master synchronization atomically.
    Returns dict of counts: inserted, updated, deleted, stored_total.
    """
    with transaction.atomic():
        # Pre-resolve/create all required designations
        all_desig_names = {
            item['designation_name'] for item in (to_create + to_update) if item.get('designation_name')
        }
        existing_desigs = {d.name: d for d in Designation.objects.all()}
        for name in all_desig_names:
            if name not in existing_desigs:
                matching_item = next((i for i in (to_create + to_update) if i['designation_name'] == name), None)
                cat = matching_item['dept_category'] if matching_item else 'Teaching'
                desig_obj = Designation.objects.create(name=name, category=cat or 'Teaching')
                existing_desigs[name] = desig_obj

        # 1. Bulk create new records
        staff_objs_create = [
            Staff(
                staff_id=item['staff_id'],
                name=item['name'],
                staff_category=item['staff_category'],
                designation=existing_desigs[item['designation_name']],
                dept_category=item['dept_category'],
                dept_name=item['dept_name'],
                mobile=item['mobile'],
                email=item['email'],
                date_of_joining=item['date_of_joining'],
                session=item['session'],
                fixed_session=item['fixed_session'],
                is_active=True,
                password=item.get('password', item['staff_id']),
                role=item['role'],
            )
            for item in to_create
        ]
        if staff_objs_create:
            Staff.objects.bulk_create(staff_objs_create, batch_size=500)

        # 2. Bulk update existing records
        staff_objs_update = [
            Staff(
                id=item['id'],
                staff_id=item['staff_id'],
                name=item['name'],
                staff_category=item['staff_category'],
                designation=existing_desigs[item['designation_name']],
                dept_category=item['dept_category'],
                dept_name=item['dept_name'],
                mobile=item['mobile'],
                email=item['email'],
                date_of_joining=item['date_of_joining'],
                session=item['session'],
                fixed_session=item['fixed_session'],
                is_active=True,
                password=item.get('password', item['staff_id']),
                role=item['role'],
            )
            for item in to_update
        ]
        if staff_objs_update:
            update_fields = [
                'name', 'staff_category', 'designation', 'dept_category',
                'dept_name', 'mobile', 'email', 'date_of_joining', 'session',
                'fixed_session', 'is_active', 'role', 'password'
            ]
            Staff.objects.bulk_update(staff_objs_update, update_fields, batch_size=500)

        # 3. Synchronize: prune records not present in the master Excel file
        deleted_count = 0
        if excel_staff_ids:
            deleted_count, _ = Staff.objects.exclude(staff_id__in=excel_staff_ids).delete()
            logger.info(f"Deleted {deleted_count} staff records not in upload")

        return {
            'inserted': len(staff_objs_create),
            'updated': len(staff_objs_update),
            'deleted': deleted_count,
            'stored_total': len(staff_objs_create) + len(staff_objs_update),
        }

@csrf_exempt
def preview_staff_upload(request):
    """
    API endpoint: reads uploaded Excel file, performs validation and duplicate detection,
    stores pending import payload in session, and returns preview records and summary JSON.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method. POST required.'}, status=405)

    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        return JsonResponse({'success': False, 'error': 'No file uploaded. Please select an Excel file (.xlsx or .xls).'}, status=400)

    try:
        df = pd.read_excel(excel_file, engine='openpyxl', dtype=str)
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Could not read Excel file: {str(e)}'}, status=400)

    result = parse_and_validate_staff_excel(df)
    if not result['valid_format']:
        return JsonResponse({
            'success': False,
            'error': f"Missing required columns: {', '.join(result['missing_columns'])}"
        }, status=400)

    # Store pending import in session for confirm step
    request.session['pending_staff_import'] = {
        'to_create': result['to_create'],
        'to_update': result['to_update'],
        'excel_staff_ids': list(result['excel_staff_ids']),
        'summary': result['summary'],
        'filename': excel_file.name,
    }

    return JsonResponse({
        'success': True,
        'filename': excel_file.name,
        'summary': result['summary'],
        'records': result['records'],
    })

@csrf_exempt
def confirm_staff_import(request):
    """
    API endpoint: commits the pre-validated staff records into the database.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method. POST required.'}, status=405)

    pending = request.session.pop('pending_staff_import', None)
    if not pending:
        return JsonResponse({
            'success': False,
            'error': 'No pending import data found or session expired. Please preview the file again.'
        }, status=400)

    to_create = pending.get('to_create', [])
    to_update = pending.get('to_update', [])
    excel_staff_ids = set(pending.get('excel_staff_ids', []))
    cached_summary = pending.get('summary', {})

    try:
        import_result = apply_staff_import(to_create, to_update, excel_staff_ids)

        stored_total = import_result['stored_total']
        inserted = import_result['inserted']
        updated = import_result['updated']
        total_rows = cached_summary.get('total_rows', stored_total)
        duplicates = cached_summary.get('duplicate_count', 0)
        errors = cached_summary.get('error_count', 0)

        msg = (
            f"Successfully stored {stored_total} staff record(s) in the database "
            f"({inserted} new, {updated} updated)."
        )
        if duplicates:
            msg += f" {duplicates} duplicate record(s) skipped."
        if errors:
            msg += f" {errors} record(s) had validation errors."

        try:
            messages.success(request, msg, fail_silently=True)
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'message': msg,
            'total_in_file': total_rows,
            'stored_in_database': stored_total,
            'created': inserted,
            'updated': updated,
            'duplicates_skipped': duplicates,
            'errors_skipped': errors,
            'summary': {
                'total_rows': total_rows,
                'successfully_processed': total_rows,
                'successfully_stored': stored_total,
                'inserted': inserted,
                'updated': updated,
                'duplicates_skipped': duplicates,
                'errors': errors,
            }
        })
    except Exception as e:
        logger.exception("Critical error during confirmed staff import")
        return JsonResponse({
            'success': False,
            'error': f'Database error during import: {str(e)}'
        }, status=500)

def staff_management(request):
    form = StaffUploadForm()
    
    # Get staff counts - moved up to ensure it's available in all contexts
    staff_counts = get_staff_counts_by_dept()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    staff_category_filter = request.GET.get('staff_category')
    dept_category_filter = request.GET.get('dept_category')
    designation_filter = request.GET.get('designation')
    department_filter = request.GET.get('department')
    
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
    
    total_filtered_count = staff_list.count()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # AJAX response
    if is_ajax:
        return render(request, 'staff/staff_table.html', {
            'staff_list': staff_list,
            'total_count': total_filtered_count,
            'search_query': search_query,
            'staff_category_filter': staff_category_filter,
            'dept_category_filter': dept_category_filter,
            'designation_filter': designation_filter,
            'department_filter': department_filter,
            'request': request,
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
    
    # File upload handling (direct form POST fallback for automated tests / non-JS)
    if request.method == 'POST':
        form = StaffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['excel_file']
                try:
                    df = pd.read_excel(excel_file, engine='openpyxl', dtype=str)
                except Exception as e:
                    logger.error(f"Error reading Excel file: {str(e)}")
                    messages.error(request, f"Error reading Excel file: {str(e)}")
                    return redirect('staff:staff-management')

                result = parse_and_validate_staff_excel(df)
                if not result['valid_format']:
                    msg = f"Missing required columns: {', '.join(result['missing_columns'])}"
                    logger.error(msg)
                    messages.error(request, msg)
                    return redirect('staff:staff-management')

                import_result = apply_staff_import(
                    result['to_create'],
                    result['to_update'],
                    result['excel_staff_ids']
                )

                summary = result['summary']
                stored_total = import_result['stored_total']
                inserted = import_result['inserted']
                updated = import_result['updated']

                if result['error_rows']:
                    request.session['upload_errors'] = result['error_rows']
                request.session['upload_summary'] = summary

                msg = (
                    f"Successfully stored {stored_total} of {summary['total_rows']} record(s) in the database "
                    f"({inserted} new, {updated} updated)."
                )
                if summary['duplicate_count']:
                    msg += f" {summary['duplicate_count']} duplicate record(s) skipped."
                if summary['error_count']:
                    msg += f" — {summary['error_count']} row(s) had errors (see details below)"
                messages.success(request, msg)
                return redirect('staff:staff-management')

            except Exception as e:
                logger.exception("Critical error during staff import")
                messages.error(request, f'System error during import: {str(e)}')
                return redirect('staff:staff-management')

    # ── Pull upload errors/summary from session (cleared after one page load) ─
    upload_errors = request.session.pop('upload_errors', [])
    upload_summary = request.session.pop('upload_summary', None)

    return render(request, 'staff/management.html', {
        'form': form,
        'staff_list': staff_list,
        'search_query': search_query,
        'messages': messages.get_messages(request),
        'staff_types': staff_types,
        'dept_categories': dept_categories,
        'departments': departments,
        'total_count': total_filtered_count,
        'request': request,
        'upload_errors': upload_errors,
        'upload_summary': upload_summary,
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
        print(f"Staff {staff_id} date_of_joining: {staff.date_of_joining}")

        # Safe date formatting handling
        doj = staff.date_of_joining
        date_of_joining = ''
        if doj:
            # If datetime.datetime, convert to date
            if hasattr(doj, 'strftime'):
                # Format strictly to 'YYYY-MM-DD'
                date_of_joining = doj.strftime('%Y-%m-%d')
            else:
                # Fallback for other types (string?)
                date_of_joining = str(doj).split(' ')[0]

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