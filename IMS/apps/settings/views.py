from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from apps.staff.models import Staff
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ..invigilation_schedule.models import InvigilationSchedule
import logging
from datetime import datetime
import pandas as pd



def settings_home(request):
    user_role = None
    if request.session.get('staff_id'):
        # Fetch staff record by staff_id from session
        staff = Staff.objects.filter(staff_id=request.session['staff_id']).first()
        if staff:
            user_role = staff.role  # Use 'role' field from DB
    return render(request, 'settings/settings.html', {'role': user_role})



@csrf_exempt  # Disable CSRF only for testing, enable in production
def change_password_no_auth(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=405)

    staff_id = request.POST.get('staff_id', '').strip()
    old_password = request.POST.get('old_password', '').strip()
    new_password = request.POST.get('new_password', '').strip()

    if not (staff_id and old_password and new_password):
        return JsonResponse({'success': False, 'message': 'Missing fields'}, status=400)

    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Staff not found'}, status=404)

    # Plain text password comparison
    if staff.password != old_password:
        print(f"Checking old password: entered='{old_password}', stored='{staff.password}'")
        return JsonResponse({'success': False, 'message': 'Old password is incorrect'}, status=400)
        

    # Update password
    staff.password = new_password
    staff.save()

    return JsonResponse({'success': True, 'message': 'Password changed successfully'})

@csrf_exempt  # Replace with proper auth and CSRF in production
def upload_schedule(request):
    if request.method != "POST" or 'file' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)

    file = request.FILES['file']

    try:
        df = pd.read_excel(file)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid Excel file'}, status=400)

    # Expected columns with possible aliases for flexible header mapping
    column_aliases = {
        "S.No": ["S.No", "S. No", "Sr. No", "Serial No", "SNo"],
        "Date": ["Date", "Schedule Date", "Exam Date"],
        "Session": ["Session", "Exam Session"],
        "Hall No": ["Hall No", "Hall Number", "Hall"],
        "Hall Department": ["Hall Department", "Hall Dept", "HallDepartment"],
        "Staff Department": ["Staff Department", "Staff Dept", "Dept Name"],
        "Staff ID": ["Staff ID", "StaffID", "Staff Id"],
        "Name": ["Name", "Staff Name", "Staff"],
        "Designation": ["Designation", "Staff Designation"],
        "Staff Category": ["Staff Category", "Category"],
        "Dept Category": ["Dept Category", "Department Category"],
        "Hall Dept Category": ["Hall Dept Category", "Hall Dept Cat"],
    }

    # Normalize columns for flexible matching
    df_cols_lower = {col.lower(): col for col in df.columns}
    rename_map = {}
    for expected_col, aliases in column_aliases.items():
        found_col = None
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in df_cols_lower:
                found_col = df_cols_lower[alias_lower]
                break
        if not found_col:
            return JsonResponse({'success': False, 'message': f'Missing column "{expected_col}"'}, status=400)
        rename_map[found_col] = expected_col
    df = df.rename(columns=rename_map)

    # Validate and convert Date column to datetime.date
    try:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Invalid Date column: {str(e)}'}, status=400)

    # Delete existing schedules matching these dates to avoid duplicates
    dates_in_file = df["Date"].unique()
    InvigilationSchedule.objects.filter(date__in=dates_in_file).delete()

    schedule_objects = []
    success_count = 0
    errors = []

    for i, row in df.iterrows():
        try:
            obj = InvigilationSchedule(
                date=row["Date"],
                session=str(row["Session"]).strip(),
                hall_no=str(row["Hall No"]).strip(),
                hall_department=str(row["Hall Department"]).strip(),
                dept_name=str(row["Staff Department"]).strip(),
                staff_id=str(row["Staff ID"]).strip(),
                name=str(row["Name"]).strip(),
                designation=str(row["Designation"]).strip(),
                staff_category=str(row["Staff Category"]).strip(),
                dept_category=str(row["Dept Category"]).strip(),
                hall_dept_category=str(row["Hall Dept Category"]).strip(),
                # Add other model fields here if needed
            )
            schedule_objects.append(obj)
            success_count += 1
        except Exception as e:
            errors.append(f"Row {i+2}: {str(e)}")  # add 2 to account for header row and zero indexing

    # Bulk create all schedule entries at once
    InvigilationSchedule.objects.bulk_create(schedule_objects)

    message = f"Successfully processed {success_count} records."
    if errors:
        message += f" Errors: {'; '.join(errors)}"

    return JsonResponse({'success': True, 'message': message})