from django.shortcuts import redirect

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.session.get('role') != role:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
