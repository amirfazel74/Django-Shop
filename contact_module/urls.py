from django.urls import path
from . import views

urlpatterns = [
    # آدرس ثبت اطلاعات گیرنده و آدرس
    path('setup-profile/', views.SetupProfileView.as_view(), name='setup-profile'),
]