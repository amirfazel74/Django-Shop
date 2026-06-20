from django.urls import path
from . import views

app_name = 'order_module'
urlpatterns = [
    path('add-to-cart/', views.add_product_to_order, name='add-product-to-order'),
    path('checkout/shipping/', views.checkout_shipping_view, name='checkout_shipping'),
    path('checkout/request-payment/', views.request_payment_view, name='request_payment'),
    path('checkout/verify-payment/', views.verify_payment_view, name='verify_payment'),
]
