from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class OTPRequest(models.Model):
    """
    جدول مدیریت درخواست‌های کد یک‌بار مصرف (OTP)
    هر بار که کاربری کد درخواست می‌دهد، یک رکورد در این جدول ساخته می‌شود.
    """

    class PurposeChoices(models.TextChoices):
        LOGIN = 'LOGIN', _('ورود و ثبت‌نام')
        CHANGE_PHONE = 'CHANGE_PHONE', _('تغییر شماره موبایل')
        TWO_FACTOR = 'TWO_FACTOR', _('احراز هویت دو مرحله‌ای')
        VERIFY_ACTION = 'VERIFY_ACTION', _('تایید عملیات حساس')

    # شماره موبایل (با ایندکس برای جستجوی سریع)
    phone_number = models.CharField(
        _("شماره موبایل"),
        max_length=15,
        db_index=True
    )

    # کد تایید (۵ رقمی) - می‌تواند تا ۱۲۸ کاراکتر باشد (برای هش احتمالی در آینده)
    otp_code = models.CharField(_("کد تایید"), max_length=128)

    # هدف از ارسال کد
    purpose = models.CharField(
        _("هدف از ارسال"),
        max_length=20,
        choices=PurposeChoices.choices,
        default=PurposeChoices.LOGIN
    )

    # اطلاعات امنیتی (برای جلوگیری از اسپم و Brute-Force)
    ip_address = models.GenericIPAddressField(
        _("آی‌پی درخواست‌دهنده"),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _("مشخصات دستگاه/مرورگر"),
        blank=True
    )

    # زمان‌بندی‌ها
    created_at = models.DateTimeField(_("زمان ایجاد"), auto_now_add=True)
    expires_at = models.DateTimeField(_("زمان انقضا"))

    # وضعیت‌ها
    is_used = models.BooleanField(_("استفاده شده"), default=False)
    failed_attempts = models.PositiveSmallIntegerField(
        _("تعداد تلاش ناموفق"),
        default=0
    )

    class Meta:
        verbose_name = _("درخواست کد تایید")
        verbose_name_plural = _("درخواست‌های کد تایید")
        ordering = ['-created_at']

        # ایندکس‌های ترکیبی برای سرعت بالا در جستجوهای امنیتی
        indexes = [
            models.Index(fields=['phone_number', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        """تخصیص خودکار زمان انقضا (۲ دقیقه) در صورت عدم مقداردهی"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    # ==========================================
    # متدهای کمکی (Properties)
    # ==========================================

    @property
    def is_expired(self):
        """آیا کد منقضی شده است؟"""
        return timezone.now() > self.expires_at

    @property
    def is_blocked(self):
        """آیا به دلیل تلاش زیاد مسدود شده است؟ (حداکثر ۳ تلاش)"""
        return self.failed_attempts >= 3

    def is_valid(self):
        """آیا این کد در حال حاضر برای استفاده معتبر است؟"""
        return not self.is_used and not self.is_expired and not self.is_blocked

    def __str__(self):
        status = (
            "استفاده شده" if self.is_used
            else ("منقضی/مسدود" if not self.is_valid() else "معتبر")
        )
        return f"{self.phone_number} ({self.get_purpose_display()}) - {status}"


class AuthSetting(models.Model):
    """
    تنظیمات کلی سیستم احراز هویت
    فقط یک ردیف از این جدول می‌تواند وجود داشته باشد (Singleton).
    """
    is_otp_enabled = models.BooleanField(
        _("ورود/ثبت‌نام پیامکی فعال باشد؟"),
        default=True
    )
    is_password_enabled = models.BooleanField(
        _("ورود با رمز عبور فعال باشد؟"),
        default=True
    )
    force_profile_completion = models.BooleanField(
        _("اجبار به تکمیل پروفایل پس از ثبت‌نام؟"),
        default=True
    )

    class Meta:
        verbose_name = _("تنظیمات احراز هویت")
        verbose_name_plural = _("تنظیمات احراز هویت")

    def clean(self):
        """جلوگیری از ساخت بیش از یک ردیف تنظیمات"""
        if AuthSetting.objects.exists() and not self.pk:
            raise ValidationError(_("فقط یک ردیف تنظیمات می‌تواند وجود داشته باشد."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "تنظیمات لاگین"
