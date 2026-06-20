from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect

from product_module.models import Product
from .models import Order, OrderDetail


# Create your views here.

def add_product_to_order(request: HttpRequest):
    # پشتیبانی از هر دو متد GET و POST
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id', 0))
        count = int(request.POST.get('count', 1))
    else:
        product_id = int(request.GET.get('product_id', 0))
        count = int(request.GET.get('count', 1))

    if count < 1:
        # اگر از کارت محصول می‌آید، به صفحه قبل برگردان
        if request.method == 'POST':
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return JsonResponse({
            'status': 'invalid_count',
            'text': 'مقدار وارد شده معتبر نمی باشد',
            'confirm_button_text': 'مرسی از شما',
            'icon': 'warning'
        })

    if request.user.is_authenticated:
        product = Product.objects.filter(id=product_id, is_active=True, is_delete=False).first()
        if product is not None:
            current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
            current_order_detail = current_order.orderdetail_set.filter(product_id=product_id).first()
            if current_order_detail is not None:
                current_order_detail.count += count
                current_order_detail.save()
            else:
                new_detail = OrderDetail(order_id=current_order.id, product_id=product_id, count=count)
                new_detail.save()

            # اگر از فرم POST می‌آید، به صفحه قبل برگردان
            if request.method == 'POST':
                return redirect(request.META.get('HTTP_REFERER', '/'))

            return JsonResponse({
                'status': 'success',
                'text': 'محصول مورد نظر با موفقیت به سبد خرید شما اضافه شد',
                'confirm_button_text': 'باشه ممنونم',
                'icon': 'success'
            })
        else:
            if request.method == 'POST':
                return redirect(request.META.get('HTTP_REFERER', '/'))
            return JsonResponse({
                'status': 'not_found',
                'text': 'محصول مورد نظر یافت نشد',
                'confirm_button_text': 'مرسییییی',
                'icon': 'error'
            })
    else:
        if request.method == 'POST':
            # اگر کاربر لاگین نکرده، به صفحه ورود هدایت شود
            return redirect('/auth/')
        return JsonResponse({
            'status': 'not_auth',
            'text': 'برای افزودن محصول به سبد خرید ابتدا می بایست وارد سایت شوید',
            'confirm_button_text': 'ورود به سایت',
            'icon': 'error'
        })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import http.client
import json
import datetime
from django.urls import reverse

@login_required
def checkout_shipping_view(request):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    
    # If cart is empty
    if not current_order.orderdetail_set.exists():
        return redirect('user_basket_page')

    if request.method == 'POST':
        # Get data from form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        province = request.POST.get('province')
        city = request.POST.get('city')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        shipping_method = request.POST.get('shipping_method') # 'post' or 'barbari'
        
        # Calculate shipping cost (mock logic)
        shipping_cost = 85000 if shipping_method == 'post' else 0
        
        # Update order
        current_order.first_name = first_name
        current_order.last_name = last_name
        current_order.mobile = mobile
        current_order.province = province
        current_order.city = city
        current_order.address = address
        current_order.postal_code = postal_code
        current_order.shipping_method = shipping_method
        current_order.shipping_cost = shipping_cost
        current_order.save()
        
        return redirect('order_module:request_payment')

    total_amount = current_order.calculate_total_price()
    context = {
        'order': current_order,
        'sum': total_amount
    }
    return render(request, 'order_module/checkout_shipping.html', context)


@login_required
def request_payment_view(request):
    current_order = Order.objects.filter(is_paid=False, user_id=request.user.id).first()
    if not current_order or not current_order.orderdetail_set.exists():
        return redirect('user_basket_page')

    # Ensure address exists
    if not current_order.address:
        return redirect('checkout_shipping')

    # Calculate final amount
    total_amount = current_order.calculate_total_price()
    final_amount_toman = total_amount + current_order.shipping_cost
    final_amount_rial = final_amount_toman * 10
    
    # Zibal request
    conn = http.client.HTTPSConnection("gateway.zibal.ir")
    
    # Generate a callback URL
    callback_url = request.build_absolute_uri(reverse('order_module:verify_payment'))
    
    payload_dict = {
        "merchant": "zibal",
        "amount": final_amount_rial,
        "callbackUrl": callback_url,
        "description": f"پرداخت سفارش #{current_order.id}",
        "orderId": str(current_order.id),
        "mobile": current_order.mobile or request.user.mobile
    }
    payload = json.dumps(payload_dict)
    
    headers = { 'Content-Type': "application/json" }
    
    try:
        conn.request("POST", "/v1/request", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))
        
        if response_data.get('result') == 100:
            track_id = response_data.get('trackId')
            current_order.payment_track_id = str(track_id)
            current_order.save()
            return redirect(f"https://gateway.zibal.ir/start/{track_id}")
        else:
            return render(request, 'order_module/payment_error.html', {
                'message': f"خطا در اتصال به درگاه پرداخت: {response_data.get('message')}"
            })
            
    except Exception as e:
        return render(request, 'order_module/payment_error.html', {
            'message': "متاسفانه مشکلی در ارتباط با درگاه پرداخت به وجود آمد."
        })


def verify_payment_view(request):
    track_id = request.GET.get('trackId')
    success = request.GET.get('success')
    status = request.GET.get('status')
    order_id = request.GET.get('orderId')
    
    if success == '1':
        # Verify from Zibal
        conn = http.client.HTTPSConnection("gateway.zibal.ir")
        payload = json.dumps({
            "merchant": "zibal",
            "trackId": track_id
        })
        headers = { 'Content-Type': "application/json" }
        
        try:
            conn.request("POST", "/v1/verify", payload, headers)
            res = conn.getresponse()
            data = res.read()
            response_data = json.loads(data.decode("utf-8"))
            
            if response_data.get('result') == 100:
                # Find the order
                current_order = Order.objects.filter(id=order_id, payment_track_id=track_id).first()
                if current_order:
                    current_order.is_paid = True
                    current_order.payment_date = datetime.datetime.now()
                    current_order.payment_ref_number = str(response_data.get('refNumber'))
                    current_order.status = 'processing'
                    current_order.save()
                    
                    # Update order details with final price
                    for detail in current_order.orderdetail_set.all():
                        detail.final_price = detail.product.price
                        detail.save()
                        
                    return render(request, 'order_module/payment_success.html', {
                        'ref_number': response_data.get('refNumber'),
                        'order_id': order_id
                    })
                else:
                    return render(request, 'order_module/payment_error.html', {
                        'message': "سفارش مورد نظر یافت نشد."
                    })
            elif response_data.get('result') == 201:
                return render(request, 'order_module/payment_error.html', {
                    'message': "این تراکنش قبلا تایید شده است."
                })
            else:
                return render(request, 'order_module/payment_error.html', {
                    'message': "پرداخت ناموفق بود یا تایید نشد."
                })
        except Exception as e:
            return render(request, 'order_module/payment_error.html', {
                'message': "خطا در تایید تراکنش با سرور."
            })
    else:
        return render(request, 'order_module/payment_error.html', {
            'message': "پرداخت توسط کاربر لغو شد یا ناموفق بود."
        })
