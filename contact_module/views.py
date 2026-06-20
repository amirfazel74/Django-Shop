from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

# فقط ایمپورت مدل‌ها (هیچ ایمپورتی از forms نداریم)
from .models import UserProfile, ContactUs


# ====================================================================
# ۱. ویوی تماس با ما (بدون نیاز به فایل فرم)
# ====================================================================
class ContactUsView(CreateView):
    model = ContactUs
    # جنگو خودش با این فیلدها فرم را در پس‌زمینه می‌سازد
    fields = ['title', 'full_name', 'email', 'message']
    template_name = 'contact_module/contact_us_page.html'
    success_url = '/contact-us/'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # اگر مدل SiteSetting را دارید، کدهای زیر را از کامنت در بیاورید:
        # from site_module.models import SiteSetting
        # setting = SiteSetting.objects.filter(is_main_setting=True).first()
        # context['site_setting'] = setting
        return context


# ====================================================================
# ۲. ویوی تکمیل پروفایل (مستقیم و بدون فرم جنگو)
# ====================================================================
class SetupProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.profile
        context = {
            'profile': profile
        }
        return render(request, 'contact_module/setup_profile_page.html', context)

    def post(self, request):
        profile = request.user.profile

        # دریافت مستقیم اطلاعات از تگ‌های input در HTML
        profile.receiver_name = request.POST.get('receiver_name')
        profile.receiver_mobile = request.POST.get('receiver_mobile')
        profile.province = request.POST.get('province')
        profile.city = request.POST.get('city')
        profile.address = request.POST.get('address')
        profile.postal_code = request.POST.get('postal_code')

        # مدیریت ذخیره تصویر در صورت آپلود
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')

        profile.save()
        return redirect('product-list')