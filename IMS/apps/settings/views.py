from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from apps.staff.models import Staff
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging


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

