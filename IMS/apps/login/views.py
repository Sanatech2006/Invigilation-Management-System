from django.shortcuts import render, redirect
from django.contrib import messages
from apps.staff.models import Staff

from django.urls import reverse


def login_view(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id', '').strip().lower()  # lowercase and strip whitespace
        password = request.POST.get('password', '').strip().lower()  # lowercase and strip whitespace

        try:
            # Case-insensitive lookup for staff_id
            user = Staff.objects.get(staff_id__iexact=staff_id)
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid USER ID')
            return render(request, 'login/login.html')

        # Compare lowercase password
        if user.password.lower() != password:
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
