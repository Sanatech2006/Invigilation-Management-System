"""
URL configuration for IMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.invigilation_schedule import views as invigilation_views
from django.conf import settings
from django.conf.urls.static import static
from apps.login.views import login_view
from apps.login.views import logout_view


urlpatterns = [
    path('', login_view, name='home'),
    
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls',namespace='dashboard')),
    path('staff/', include('apps.staff.urls')),
    path('student/', include('apps.student.urls')),
    path('hall/', include('apps.hall.urls')),
    path('exam-dates/', include('apps.exam_dates.urls', namespace='exam_dates')),
    path('', include('invigilation_settings.urls')),
    path('view-schedule/', include('apps.view_schedule.urls')),
    path('api/schedule/', invigilation_views.schedule_api, name='schedule_api'),
    path('manual-assignment/', include('apps.manual_assignment.urls')),
    path('', include('apps.login.urls')),  
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('settings/', include('apps.settings.urls')),
    path('logout/', logout_view, name='logout'),
    
    
    

    # Add other apps here
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
