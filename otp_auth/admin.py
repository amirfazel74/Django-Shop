from django.contrib import admin
from .models import OTPRequest, AuthSetting


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'purpose', 'is_used', 'failed_attempts', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('phone_number', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('phone_number', 'otp_code', 'purpose')
        }),
        ('اطلاعات امنیتی', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('زمان‌بندی و وضعیت', {
            'fields': ('created_at', 'expires_at', 'is_used', 'failed_attempts')
        }),
    )


@admin.register(AuthSetting)
class AuthSettingAdmin(admin.ModelAdmin):
    list_display = ('is_otp_enabled', 'is_password_enabled', 'force_profile_completion')

    def has_add_permission(self, request):
        # جلوگیری از ساخت بیش از یک ردیف
        if AuthSetting.objects.exists():
            return False
        return super().has_add_permission(request)
