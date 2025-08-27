def user_role(request):
    return {'user_role': request.session.get('role')}