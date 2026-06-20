from django.urls import path
from . import views

app_name = 'otp_auth'

urlpatterns = [
    path('', views.auth_step_one_view, name='auth_page'),
    path('request-otp/', views.auth_step_one_view, name='request_otp'),
    path('force-otp/', views.force_send_otp_view, name='force_otp'),
    path('verify-password/', views.verify_password_view, name='verify_password'),
    path('verify-otp/', views.verify_otp_and_check_profile_view, name='verify_otp'),
    path('save-profile/', views.save_initial_profile_view, name='save_profile'),
    path('logout/', views.logout_view, name='logout'),
]