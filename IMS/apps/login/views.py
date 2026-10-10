import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from apps.staff.models import Staff


def normalize_date_str(val):
    """Normalize date value/string to YYYY-MM-DD for consistent comparison."""
    if not val:
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


def get_post_data(request):
    """Extract POST data supporting both form-encoded and JSON bodies."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8'))
        except Exception:
            return {}
    return request.POST


def login_view(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            # Case-insensitive lookup for staff_id
            user = Staff.objects.get(staff_id__iexact=staff_id)
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid USER ID')
            return render(request, 'login/login.html')

        # Check password using Django's password hasher (make_password / check_password)
        # with fallback to plaintext for legacy unhashed staff records
        password_valid = False
        if user.password:
            # Check hashed password
            if check_password(password, user.password):
                password_valid = True
            elif check_password(password.lower(), user.password):
                password_valid = True
            # Check legacy plain text
            elif user.password == password or user.password.lower() == password.lower():
                password_valid = True

        if not password_valid:
            messages.error(request, 'Wrong Password')
            return render(request, 'login/login.html')

        # Successful login: store session data
        request.session['staff_id'] = user.staff_id
        request.session['role'] = user.role

        # Redirect all roles to the same dashboard page
        return redirect(reverse('dashboard:dashboard'))

    return render(request, 'login/login.html')


def logout_view(request):
    request.session.flush()  # Clear all session data
    return redirect('login')


def forgot_password_verify(request):
    """Validate Staff ID and Date of Joining against existing database records."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method is allowed.'}, status=405)

    data = get_post_data(request)
    staff_id = data.get('staff_id', '').strip()
    raw_doj = data.get('date_of_joining', '') or data.get('doj', '')
    doj = str(raw_doj).strip() if raw_doj else ''

    if not staff_id or not doj:
        return JsonResponse({'success': False, 'message': 'Please provide both Staff ID and Date of Joining.'}, status=400)

    try:
        staff = Staff.objects.get(staff_id__iexact=staff_id)
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid Staff ID or Date of Joining.'}, status=400)

    stored_doj = normalize_date_str(staff.date_of_joining)
    entered_doj = normalize_date_str(doj)

    if not stored_doj or stored_doj != entered_doj:
        return JsonResponse({'success': False, 'message': 'Invalid Staff ID or Date of Joining.'}, status=400)

    return JsonResponse({
        'success': True,
        'message': 'Identity verified successfully.',
        'staff_id': staff.staff_id,
        'name': staff.name,
    })


def forgot_password_reset(request):
    """Verify credentials again and securely reset password using Django's password hasher."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method is allowed.'}, status=405)

    data = get_post_data(request)
    staff_id = data.get('staff_id', '').strip()
    raw_doj = data.get('date_of_joining', '') or data.get('doj', '')
    doj = str(raw_doj).strip() if raw_doj else ''
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not staff_id or not doj:
        return JsonResponse({'success': False, 'message': 'Please provide Staff ID and Date of Joining.'}, status=400)

    if not new_password or not confirm_password:
        return JsonResponse({'success': False, 'message': 'Please provide both new password and confirm password.'}, status=400)

    try:
        staff = Staff.objects.get(staff_id__iexact=staff_id)
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid Staff ID or Date of Joining.'}, status=400)

    stored_doj = normalize_date_str(staff.date_of_joining)
    entered_doj = normalize_date_str(doj)

    if not stored_doj or stored_doj != entered_doj:
        return JsonResponse({'success': False, 'message': 'Invalid Staff ID or Date of Joining.'}, status=400)

    if new_password != confirm_password:
        return JsonResponse({'success': False, 'message': 'New password and confirm password do not match.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)

    # Securely hash and save new password
    staff.password = make_password(new_password)
    staff.save(update_fields=['password'])

    # If linked to Django auth User, update password there too
    if staff.user:
        staff.user.set_password(new_password)
        staff.user.save(update_fields=['password'])

    return JsonResponse({
        'success': True,
        'message': 'Password reset successfully! You can now log in with your new password.',
        'staff_id': staff.staff_id,
    })

