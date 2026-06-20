from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# ==========================================
# 1. تنظیمات هسته و هشدارها (Core Configurations)
# ==========================================
class SMSConfiguration(models.Model):
    """الگوی سینگلتون: فقط یک ردیف تنظیمات می‌تواند در سیستم وجود داشته باشد"""
    api_key = models.CharField(_("کلید API (X-API-KEY)"), max_length=255)
    low_credit_threshold = models.DecimalField(_("آستانه هشدار شارژ (تومان)"), max_digits=12, decimal_places=0,
                                               default=100000)
    is_active = models.BooleanField(_("سیستم پیامکی فعال باشد؟"), default=True,
                                    help_text=_("برای قطع اضطراری کل پیامک‌های سایت"))
    updated_at = models.DateTimeField(_("آخرین بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات درگاه پیامک")
        verbose_name_plural = _("تنظیمات درگاه پیامک")


    def save(self, *args, **kwargs):
        """الگوی سینگلتون: شناسه را همیشه روی 1 تنظیم می‌کنیم تا ردیف جدیدی ساخته نشود و قبلی آپدیت شود"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """جلوگیری از حذف تنظیمات اصلی"""
        pass

    def __str__(self):
        return "تنظیمات اصلی سامانه پیامک"


class AdminAlertNumber(models.Model):
    name = models.CharField(_("نام مدیر"), max_length=100)
    phone_number = models.CharField(_("شماره موبایل"), max_length=11)
    receive_daily_reports = models.BooleanField(_("دریافت گزارش روزانه"), default=True)
    receive_low_credit_alerts = models.BooleanField(_("دریافت هشدار اتمام شارژ"), default=True)
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        verbose_name = _("شماره ادمین (هشدارها)")
        verbose_name_plural = _("شماره‌های ادمین (هشدارها)")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


# ==========================================
# 2. مدیریت خطوط و قالب‌ها (Lines & Templates)
# ==========================================
class SMSLine(models.Model):
    number = models.CharField(_("شماره خط"), max_length=20, unique=True, help_text=_("مثلا: 30004505000017"))
    title = models.CharField(_("عنوان خط"), max_length=100, help_text=_("مثلا: خط اطلاع‌رسانی"))
    is_active = models.BooleanField(_("فعال"), default=True)
    is_default_for_bulk = models.BooleanField(_("خط پیش‌فرض ارسال گروهی"), default=False)
    is_default_for_p2p = models.BooleanField(_("خط پیش‌فرض ارسال نظیر به نظیر"), default=False)

    class Meta:
        verbose_name = _("خط پیامکی")
        verbose_name_plural = _("خطوط پیامکی")

    def clean(self):
        """جلوگیری از انتخاب چند خط به عنوان پیش‌فرض"""
        if self.is_default_for_bulk:
            SMSLine.objects.filter(is_default_for_bulk=True).exclude(pk=self.pk).update(is_default_for_bulk=False)
        if self.is_default_for_p2p:
            SMSLine.objects.filter(is_default_for_p2p=True).exclude(pk=self.pk).update(is_default_for_p2p=False)

    def __str__(self):
        return f"{self.title} - {self.number}"


class SMSTemplate(models.Model):
    internal_name = models.CharField(_("نام سیستمی قالب"), max_length=100, unique=True,
                                     help_text=_("نام ثابت در کد مثل OTP_LOGIN"))
    template_id = models.IntegerField(_("کد قالب در sms.ir"), help_text=_("شناسه عددی قالب"))
    body_preview = models.TextField(_("پیش‌نمایش متن قالب"), help_text=_("مثلا: کد ورود شما #Code# می‌باشد."))
    required_parameters = models.JSONField(_("متغیرهای اجباری"), default=list, help_text=_('مثال: ["Code", "Name"]'))
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        verbose_name = _("قالب خدماتی (Verify)")
        verbose_name_plural = _("قالب‌های خدماتی")

    def __str__(self):
        return self.internal_name


# ==========================================
# 3. مدیریت ارسال‌های گروهی و زمان‌بندی شده
# ==========================================
class ScheduledPack(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('در انتظار ارسال')
        SENT = 'SENT', _('ارسال شده')
        CANCELED = 'CANCELED', _('لغو شده')
        FAILED = 'FAILED', _('خطا در سامانه')

    pack_id = models.CharField(_("شناسه بسته (sms.ir)"), max_length=100, unique=True, blank=True, null=True)
    line = models.ForeignKey(SMSLine, on_delete=models.PROTECT, verbose_name=_("خط ارسالی"))
    total_recipients = models.IntegerField(_("تعداد مخاطبین"), default=0)
    total_cost = models.DecimalField(_("هزینه کل (تومان)"), max_digits=10, decimal_places=0, default=0)
    scheduled_datetime = models.DateTimeField(_("زمان مقرر برای ارسال"), blank=True, null=True)
    status = models.CharField(_("وضعیت بسته"), max_length=20, choices=StatusChoices.choices,
                              default=StatusChoices.PENDING)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)

    class Meta:
        verbose_name = _("بسته پیامک زمان‌بندی شده")
        verbose_name_plural = _("بسته‌های پیامک زمان‌بندی شده")

    def __str__(self):
        return f"بسته {self.pack_id or 'ثبت نشده'} - {self.get_status_display()}"


# ==========================================
# 4. لاگ‌ها و گزارش‌گیری جامع (Logs)
# ==========================================
class OutboundSMSLog(models.Model):
    class SendTypeChoices(models.TextChoices):
        VERIFY = 'VERIFY', _('خدماتی (Verify)')
        BULK = 'BULK', _('گروهی (Bulk)')
        P2P = 'P2P', _('نظیر به نظیر (P2P)')

    class DeliveryStateChoices(models.IntegerChoices):
        DELIVERED = 1, _('رسیده به گوشی')
        NOT_DELIVERED = 2, _('نرسیده به گوشی')
        REACHED_TELECOM = 3, _('رسیده به مخابرات')
        NOT_REACHED_TELECOM = 4, _('نرسیده به مخابرات')
        REACHED_OPERATOR = 5, _('رسیده به اپراتور')
        FAILED = 6, _('ناموفق')
        BLACKLIST = 7, _('لیست سیاه')
        UNKNOWN = 8, _('نامشخص')

    message_id = models.BigIntegerField(_("شناسه پیامک (sms.ir)"), unique=True, null=True, blank=True)
    pack = models.ForeignKey(ScheduledPack, on_delete=models.CASCADE, null=True, blank=True, related_name='messages',
                             verbose_name=_("بسته مرتبط"))
    template = models.ForeignKey(SMSTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_("قالب استفاده شده"))
    line = models.ForeignKey(SMSLine, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name=_("خط ارسال‌کننده"))

    mobile = models.CharField(_("شماره مقصد"), max_length=15)
    message_text = models.TextField(_("متن پیامک"))
    cost = models.DecimalField(_("هزینه (تومان)"), max_digits=8, decimal_places=0, null=True, blank=True)

    send_type = models.CharField(_("نوع ارسال"), max_length=10, choices=SendTypeChoices.choices)
    delivery_state = models.IntegerField(_("وضعیت دلیوری"), choices=DeliveryStateChoices.choices, null=True, blank=True)
    delivery_datetime = models.DateTimeField(_("زمان دلیوری"), null=True, blank=True)
    sent_at = models.DateTimeField(_("زمان ارسال"), auto_now_add=True)

    class Meta:
        verbose_name = _("تاریخچه ارسال")
        verbose_name_plural = _("تاریخچه ارسال‌ها")
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.mobile} - {self.get_send_type_display()}"


class InboundSMSLog(models.Model):
    receive_id = models.BigIntegerField(_("شناسه دریافت (sms.ir)"), unique=True)
    line = models.ForeignKey(SMSLine, on_delete=models.SET_NULL, null=True, verbose_name=_("خط دریافت‌کننده"))
    sender_mobile = models.CharField(_("شماره فرستنده"), max_length=15)
    message_text = models.TextField(_("متن پیامک"))
    received_at = models.DateTimeField(_("زمان دریافت (از سامانه)"))
    is_processed = models.BooleanField(_("پردازش شده توسط سیستم؟"), default=False)
    created_at = models.DateTimeField(_("تاریخ ثبت در سایت"), auto_now_add=True)

    class Meta:
        verbose_name = _("پیامک دریافتی")
        verbose_name_plural = _("پیامک‌های دریافتی")
        ordering = ['-received_at']

    def __str__(self):
        return f"از {self.sender_mobile} - پردازش: {self.is_processed}"