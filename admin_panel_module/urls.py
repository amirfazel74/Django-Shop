from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_panel_dashboard, name='admin_panel_dashboard'),
    path('orders/', views.admin_orders_list, name='admin_orders_list'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
]
