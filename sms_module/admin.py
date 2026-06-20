from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    SMSConfiguration, AdminAlertNumber, SMSLine,
    SMSTemplate, ScheduledPack, OutboundSMSLog, InboundSMSLog
)


# ==========================================
# 1. تنظیمات هسته (Singleton)
# ==========================================
@admin.register(SMSConfiguration)
class SMSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'low_credit_threshold', 'is_active', 'updated_at')

    def has_add_permission(self, request):
        # جلوگیری از ساخت بیش از یک ردیف تنظیمات
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # تنظیمات اصلی هرگز نباید پاک شوند
        return False


@admin.register(AdminAlertNumber)
class AdminAlertNumberAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'receive_daily_reports', 'receive_low_credit_alerts', 'is_active')
    list_editable = ('is_active', 'receive_daily_reports', 'receive_low_credit_alerts')
    search_fields = ('name', 'phone_number')


# ==========================================
# 2. خطوط و قالب‌ها
# ==========================================
@admin.register(SMSLine)
class SMSLineAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'is_default_for_bulk', 'is_default_for_p2p', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title', 'number')
    list_filter = ('is_active', 'is_default_for_bulk', 'is_default_for_p2p')


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'template_id', 'is_active')
    search_fields = ('internal_name', 'template_id')
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('internal_name', 'template_id', 'is_active')}),
        (_('جزئیات قالب'), {'fields': ('body_preview', 'required_parameters')}),
    )


# ==========================================
# 3. مدیریت بسته‌های زمان‌بندی شده
# ==========================================
@admin.register(ScheduledPack)
class ScheduledPackAdmin(admin.ModelAdmin):
    list_display = ('pack_id', 'line', 'total_recipients', 'scheduled_datetime', 'status', 'created_at')
    list_filter = ('status', 'line', 'scheduled_datetime')
    search_fields = ('pack_id',)
    readonly_fields = ('created_at',)

    actions = ['cancel_scheduled_packs']

    @admin.action(description=_("لغو بسته‌های در انتظار ارسال"))
    def cancel_scheduled_packs(self, request, queryset):
        # فقط بسته‌هایی که هنوز ارسال نشده‌اند را می‌توان لغو کرد
        pending_packs = queryset.filter(status=self.model.StatusChoices.PENDING)
        count = pending_packs.count()

        # نکته: در مرحله بعد (services.py) منطق اتصال به API برای حذف واقعی در sms.ir را اینجا اضافه می‌کنیم
        pending_packs.update(status=self.model.StatusChoices.CANCELED)

        self.message_user(request, f"{count} بسته زمان‌بندی شده با موفقیت لغو شد.")


# ==========================================
# 4. لاگ‌های امنیتی (فقط خواندنی)
# ==========================================
class ReadOnlyAdminMixin:
    """میکسین حرفه‌ای برای غیرفعال کردن ساخت، ویرایش و حذف در پنل ادمین"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OutboundSMSLog)
class OutboundSMSLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('mobile', 'send_type', 'delivery_state', 'cost', 'sent_at')
    list_filter = ('send_type', 'delivery_state', 'line', 'sent_at')
    search_fields = ('mobile', 'message_id', 'pack__pack_id')
    readonly_fields = (
        'message_id', 'pack', 'template', 'line', 'mobile',
        'message_text', 'cost', 'send_type', 'delivery_state',
        'delivery_datetime', 'sent_at'
    )

    fieldsets = (
        (_('اطلاعات مقصد'), {'fields': ('mobile', 'message_text')}),
        (_('اطلاعات سیستمی'), {'fields': ('send_type', 'template', 'pack', 'line')}),
        (_('وضعیت و هزینه'), {'fields': ('delivery_state', 'delivery_datetime', 'cost', 'message_id', 'sent_at')}),
    )


@admin.register(InboundSMSLog)
class InboundSMSLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('sender_mobile', 'line', 'is_processed', 'received_at')
    list_filter = ('is_processed', 'line', 'received_at')
    search_fields = ('sender_mobile', 'receive_id', 'message_text')
    readonly_fields = (
    'receive_id', 'line', 'sender_mobile', 'message_text', 'received_at', 'is_processed', 'created_at')