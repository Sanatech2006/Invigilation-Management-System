from apps.settings.models import GlobalSettings

def user_role(request):
    try:
        settings = GlobalSettings.get_settings()
        display_reports = settings.display_reports_to_staff
    except:
        display_reports = False
        
    return {
        'user_role': request.session.get('role'),
        'display_reports_to_staff': display_reports
    }