from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from order_module.models import Order
from account_module.models import User
from product_module.models import Product

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_panel_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    total_users = User.objects.count()
    
    # Calculate total revenue
    paid_orders = Order.objects.filter(is_paid=True)
    total_revenue = sum([order.calculate_total_price() for order in paid_orders])
    
    latest_orders = Order.objects.order_by('-id')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'latest_orders': latest_orders
    }
    return render(request, 'admin_panel_module/admin_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def admin_orders_list(request):
    orders = Order.objects.all().order_by('-id')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    context = {
        'orders': orders,
        'current_status': status_filter
    }
    return render(request, 'admin_panel_module/admin_orders_list.html', context)

@login_required
@user_passes_test(is_superuser)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        tracking_code = request.POST.get('tracking_code')
        
        if new_status:
            order.status = new_status
        if tracking_code is not None:
            order.tracking_code = tracking_code
            
        order.save()
        return redirect('admin_order_detail', order_id=order.id)

    context = {
        'order': order,
        'sum': order.calculate_total_price()
    }
    return render(request, 'admin_panel_module/admin_order_detail.html', context)

@login_required
@user_passes_test(is_superuser)
def admin_panel_menu_component(request):
    return render(request, 'admin_panel_module/components/admin_panel_menu.html')
