from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from account_module.models import User
from order_module.models import Order, OrderDetail
from .forms import EditProfileModelForm, ChangePasswordForm
from django.contrib.auth import logout


class UserPanelDashboardPage(LoginRequiredMixin, TemplateView):
    template_name = 'user_panel_module/user_panel_dashboard_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from order_module.models import Order
        
        # Get user's orders (excluding cart)
        orders = Order.objects.filter(user_id=self.request.user.id, is_paid=True).order_by('-payment_date')
        
        context['pending_orders_count'] = orders.filter(status='pending').count()
        context['processing_orders_count'] = orders.filter(status='processing').count()
        context['shipped_orders_count'] = orders.filter(status='shipped').count()
        context['delivered_orders_count'] = orders.filter(status='delivered').count()
        
        # Total active orders (processing + shipped)
        context['active_orders_count'] = context['processing_orders_count'] + context['shipped_orders_count']
        
        context['recent_orders'] = orders[:5]
        
        return context


class UserPanelOrdersPage(LoginRequiredMixin, TemplateView):
    template_name = 'user_panel_module/user_orders_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from order_module.models import Order
        
        # Get user's orders (excluding cart)
        orders = Order.objects.filter(user_id=self.request.user.id, is_paid=True).order_by('-payment_date')
        
        context['active_orders'] = orders.filter(status__in=['pending', 'processing', 'shipped'])
        context['delivered_orders'] = orders.filter(status='delivered')
        context['canceled_orders'] = orders.filter(status='canceled')
        
        return context


class EditUserProfilePage(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(instance=current_user)
        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'user_panel_module/edit_profile_page.html', context)

    def post(self, request: HttpRequest):
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(request.POST, request.FILES, instance=current_user)
        if edit_form.is_valid():
            edit_form.save(commit=True)

        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'user_panel_module/edit_profile_page.html', context)


class ChangePasswordPage(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        context = {
            'form': ChangePasswordForm()
        }
        return render(request, 'user_panel_module/change_password_page.html', context)

    def post(self, request: HttpRequest):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_user: User = User.objects.filter(id=request.user.id).first()
            if current_user.check_password(form.cleaned_data.get('current_password')):
                current_user.set_password(form.cleaned_data.get('password'))
                current_user.save()
                logout(request)
                return redirect('/auth/')
            else:
                form.add_error('password', 'کلمه عبور وارد شده اشتباه می باشد')

        context = {
            'form': form
        }
        return render(request, 'user_panel_module/change_password_page.html', context)


def user_panel_menu_component(request: HttpRequest):
    return render(request, 'user_panel_module/components/user_panel_menu_component.html')


@login_required
def user_basket(request: HttpRequest):
    current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = current_order.calculate_total_price()

    context = {
        'order': current_order,
        'sum': total_amount
    }
    return render(request, 'user_panel_module/user_basket.html', context)


@login_required
@require_POST
def remove_order_detail(request):
    detail_id = request.POST.get('detail_id')
    if detail_id is None:
        return JsonResponse({
            'status': 'not_found_detail_id'
        })

    deleted_count, deleted_dict = OrderDetail.objects.filter(id=detail_id, order__is_paid=False, order__user_id=request.user.id).delete()

    if deleted_count == 0:
        return JsonResponse({
            'status': 'detail_not_found'
        })

    current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = current_order.calculate_total_price()

    context = {
        'order': current_order,
        'sum': total_amount
    }
    return JsonResponse({
        'status': 'success',
        'body': render_to_string('user_panel_module/user_basket_content.html', context)
    })


@login_required
@require_POST
def change_order_detail_count(request: HttpRequest):
    detail_id = request.POST.get('detail_id')
    state = request.POST.get('state')
    if detail_id is None or state is None:
        return JsonResponse({
            'status': 'not_found_detail_or_state'
        })

    order_detail = OrderDetail.objects.filter(id=detail_id, order__user_id=request.user.id, order__is_paid=False).first()

    if order_detail is None:
        return JsonResponse({
            'status': 'detail_not_found'
        })

    if state == 'increase':
        order_detail.count += 1
        order_detail.save()
    elif state == 'decrease':
        if order_detail.count == 1:
            order_detail.delete()
        else:
            order_detail.count -= 1
            order_detail.save()
    else:
        return JsonResponse({
            'status': 'state_invalid'
        })

    current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = current_order.calculate_total_price()

    context = {
        'order': current_order,
        'sum': total_amount
    }
    return JsonResponse({
        'status': 'success',
        'body': render_to_string('user_panel_module/user_basket_content.html', context)
    })
