from django.urls import path
from .views import login_view, logout_view, forgot_password_verify, forgot_password_reset


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/verify/', forgot_password_verify, name='forgot_password_verify'),
    path('forgot-password/reset/', forgot_password_reset, name='forgot_password_reset'),
]
