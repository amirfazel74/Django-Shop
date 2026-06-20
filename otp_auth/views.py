from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import AuthSetting
from .services import OTPAuthService
from contact_module.models import UserProfile
from utils.http_service import get_client_ip
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__)
User = get_user_model()


# ====================================================================
# مرحله ۱: دریافت شماره موبایل
# ====================================================================
@require_http_methods(["GET", "POST"])
def auth_step_one_view(request):
    """
    مرحله اول: دریافت شماره موبایل و تصمیم‌گیری
    - اگر کاربر قدیمی است و رمز دارد → فرم رمز عبور
    - اگر کاربر جدید است یا رمز ندارد → ارسال کد OTP
    """

    # اگر کاربر قبلاً لاگین کرده، به صفحه اصلی برگردان
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'otp_auth/auth_page.html')

    if request.method == 'POST':
        # دریافت و استانداردسازی شماره موبایل
        raw_mobile = request.POST.get('mobile', '')
        mobile = raw_mobile.strip().replace(" ", "").replace("+", "").replace("-", "")

        # تبدیل فرمت‌های مختلف به 09xxxxxxxxx
        if mobile.startswith("98") and len(mobile) == 12:
            mobile = "0" + mobile[2:]
        elif mobile.startswith("9") and len(mobile) == 10:
            mobile = "0" + mobile

        # اعتبارسنجی فرمت شماره
        if not mobile.startswith("09") or len(mobile) != 11:
            return render(request, 'otp_auth/partials/phone_form.html', {
                'error': 'شماره موبایل نامعتبر است. لطفاً به فرمت 09xxxxxxxxx وارد کنید.',
                'mobile': raw_mobile
            })

        # ذخیره در session
        request.session['auth_mobile'] = mobile

        # بررسی تنظیمات احراز هویت
        settings = AuthSetting.objects.first()
        otp_enabled = settings.is_otp_enabled if settings else True
        password_enabled = settings.is_password_enabled if settings else True

        # بررسی وجود کاربر
        user = User.objects.filter(mobile=mobile).first()

        # اگر کاربر قدیمی است و رمز عبور دارد
        if user and user.has_usable_password() and password_enabled:
            return render(request, 'otp_auth/partials/password_form.html', {
                'mobile': mobile
            })

        # در غیر این صورت، کد OTP ارسال کن
        if otp_enabled:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            result = OTPAuthService.request_otp(
                phone_number=mobile,
                purpose='LOGIN',
                ip_address=ip_address,
                user_agent=user_agent
            )

            if result['success']:
                return render(request, 'otp_auth/partials/otp_form.html', {
                    'mobile': mobile,
                    'message': result['message']
                })
            else:
                return render(request, 'otp_auth/partials/phone_form.html', {
                    'error': result['message'],
                    'mobile': mobile
                })
        else:
            return render(request, 'otp_auth/partials/phone_form.html', {
                'error': 'سیستم ورود موقتاً غیرفعال است. لطفاً بعداً تلاش کنید.'
            })


# ====================================================================
# مرحله ۲: ارسال مجدد کد OTP (وقتی کاربر رمز را فراموش کرده)
# ====================================================================
@require_http_methods(["POST"])
def force_send_otp_view(request):
    """
    وقتی کاربر رمز را فراموش کرده و درخواست ورود پیامکی می‌دهد
    """
    mobile = request.session.get('auth_mobile')

    if not mobile:
        return render(request, 'otp_auth/partials/phone_form.html', {
            'error': 'نشست شما منقضی شده است. لطفاً مجدداً تلاش کنید.'
        })

    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    result = OTPAuthService.request_otp(
        phone_number=mobile,
        purpose='LOGIN',
        ip_address=ip_address,
        user_agent=user_agent
    )

    if result['success']:
        return render(request, 'otp_auth/partials/otp_form.html', {
            'mobile': mobile,
            'message': result['message']
        })
    else:
        return render(request, 'otp_auth/partials/password_form.html', {
            'mobile': mobile,
            'error': result['message']
        })


# ====================================================================
# مرحله ۳: بررسی رمز عبور (برای کاربران قدیمی)
# ====================================================================
@require_http_methods(["POST"])
def verify_password_view(request):
    """
    بررسی رمز عبور برای کاربران قدیمی
    """
    mobile = request.session.get('auth_mobile')
    password = request.POST.get('password')

    if not mobile:
        return render(request, 'otp_auth/partials/phone_form.html', {
            'error': 'نشست شما منقضی شده است. لطفاً مجدداً تلاش کنید.'
        })

    try:
        user = User.objects.get(mobile=mobile)

        # بررسی رمز عبور
        if user.check_password(password):
            # لاگین کاربر
            login(request, user)
            logger.info(f"User {mobile} logged in with password")

            # ریدایرکت به صفحه اصلی
            return HttpResponse(headers={'HX-Redirect': '/'})
        else:
            logger.warning(f"Invalid password attempt for {mobile}")
            return render(request, 'otp_auth/partials/password_form.html', {
                'mobile': mobile,
                'error': 'رمز عبور اشتباه است.'
            })

    except User.DoesNotExist:
        return render(request, 'otp_auth/partials/phone_form.html', {
            'error': 'کاربری با این شماره یافت نشد.'
        })


# ====================================================================
# مرحله ۴: تایید کد OTP و بررسی پروفایل
# ====================================================================
@require_http_methods(["POST"])
def verify_otp_and_check_profile_view(request):
    """
    مرحله تایید پیامک:
    - اگر کاربر قدیمی است → لاگین
    - اگر کاربر جدید است → فرم تکمیل پروفایل
    """
    mobile = request.session.get('auth_mobile')
    otp_code = request.POST.get('otp_code')

    if not mobile:
        return render(request, 'otp_auth/partials/phone_form.html', {
            'error': 'نشست شما منقضی شده است. لطفاً مجدداً تلاش کنید.'
        })

    # اعتبارسنجی کد OTP
    result = OTPAuthService.verify_otp(
        phone_number=mobile,
        provided_code=otp_code,
        purpose='LOGIN'
    )

    if result['success']:
        # بررسی وجود کاربر
        user = User.objects.filter(mobile=mobile).first()

        if user:
            # کاربر قدیمی - لاگین
            login(request, user)
            logger.info(f"User {mobile} logged in with OTP")
            return HttpResponse(headers={'HX-Redirect': '/'})
        else:
            # کاربر جدید - ذخیره شماره تایید شده در session
            request.session['verified_mobile'] = mobile
            return render(request, 'otp_auth/partials/complete_profile_form.html', {
                'mobile': mobile
            })

    # کد اشتباه یا منقضی شده
    return render(request, 'otp_auth/partials/otp_form.html', {
        'error': result['message'],
        'mobile': mobile
    })


# ====================================================================
# مرحله ۵: ذخیره پروفایل اولیه (برای کاربران جدید)
# ====================================================================
@require_http_methods(["POST"])
def save_initial_profile_view(request):
    """
    ذخیره اطلاعات پروفایل برای کاربران جدید
    """
    verified_mobile = request.session.get('verified_mobile')

    if not verified_mobile:
        return render(request, 'otp_auth/partials/complete_profile_form.html', {
            'error': 'نشست منقضی شده است. لطفاً مجدداً تلاش کنید.'
        })

    # دریافت داده‌ها از فرم
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()

    # ==========================================
    # اعتبارسنجی‌ها
    # ==========================================

    # بررسی رمز عبور
    if not password or len(password) < 6:
        return render(request, 'otp_auth/partials/complete_profile_form.html', {
            'error': 'رمز عبور باید حداقل ۶ کاراکتر باشد.',
            'mobile': verified_mobile
        })

    if password != password_confirm:
        return render(request, 'otp_auth/partials/complete_profile_form.html', {
            'error': 'رمز عبور و تکرار آن مطابقت ندارند.',
            'mobile': verified_mobile
        })

    # بررسی نام و نام خانوادگی
    if not first_name or not last_name:
        return render(request, 'otp_auth/partials/complete_profile_form.html', {
            'error': 'نام و نام خانوادگی الزامی است.',
            'mobile': verified_mobile
        })

    # ==========================================
    # ساخت کاربر و پروفایل
    # ==========================================
    try:
        with transaction.atomic():
            from django.utils.crypto import get_random_string

            # ساخت کاربر
            user = User.objects.create(
                mobile=verified_mobile,
                username=verified_mobile,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                email_active_code=get_random_string(72)
            )

            # تنظیم رمز عبور
            user.set_password(password)
            user.save()

            # ساخت پروفایل (اگر وجود نداشته باشد)
            profile, created = UserProfile.objects.get_or_create(user=user)

            # ذخیره اطلاعات اضافی پروفایل (اختیاری)
            province = request.POST.get('province', '')
            city = request.POST.get('city', '')
            address = request.POST.get('address', '')

            if province:
                profile.province = province
            if city:
                profile.city = city
            if address:
                profile.address = address

            profile.save()

            # لاگین کاربر
            login(request, user)

            # پاک کردن session
            if 'verified_mobile' in request.session:
                del request.session['verified_mobile']
            if 'auth_mobile' in request.session:
                del request.session['auth_mobile']

            logger.info(f"New user registered: {verified_mobile} ({first_name} {last_name})")

            # ریدایرکت به صفحه اصلی
            return HttpResponse(headers={'HX-Redirect': '/'})

    except Exception as e:
        logger.error(f"Error creating user {verified_mobile}: {str(e)}")
        return render(request, 'otp_auth/partials/complete_profile_form.html', {
            'error': 'خطایی رخ داد. لطفاً دوباره تلاش کنید.',
            'mobile': verified_mobile
        })


# ====================================================================
# خروج کاربر
# ====================================================================
@require_http_methods(["POST", "GET"])
def logout_view(request):
    """
    خروج کاربر از سیستم
    """
    if request.user.is_authenticated:
        logger.info(f"User {request.user.mobile} logged out")
        logout(request)

    return redirect('/')


# ====================================================================
# ویو کمکی: بررسی وضعیت احراز هویت (برای API)
# ====================================================================
@login_required
def check_auth_status(request):
    """
    بررسی وضعیت احراز هویت کاربر (برای درخواست‌های AJAX)
    """
    return JsonResponse({
        'is_authenticated': True,
        'mobile': request.user.mobile,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })