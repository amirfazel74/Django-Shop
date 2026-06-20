from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.exceptions import NotRegistered # <--- این ایمپورت اضافه شد
from .models import ContactUs, UserProfile

# ====================================================================
# مدیریت تماس با ما
# ====================================================================
@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_name', 'email', 'is_read_by_admin', 'created_date')
    list_filter = ('is_read_by_admin', 'created_date')
    search_fields = ('title', 'full_name', 'email', 'message')

# ====================================================================
# چسباندن پروفایل به تنظیمات کاربر جنگو (Inline)
# ====================================================================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات گیرنده و آدرس (پروفایل)'

    # گروه‌بندی فیلدها برای زیبایی در پنل ادمین
    fieldsets = (
        ('تصویر', {
            'fields': ('image',)
        }),
        ('آدرس پیش‌فرض ارسال', {
            'fields': (
                ('receiver_name', 'receiver_mobile'),
                ('province', 'city'),
                'address',
                'postal_code'
            )
        }),
    )

# ====================================================================
# لغو ثبت کاربر پیش‌فرض با مدیریت خطا (اینجا اصلاح شد)
# ====================================================================
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')