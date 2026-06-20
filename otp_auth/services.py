import secrets
import string
from django.utils import timezone
from datetime import timedelta
import logging
from .models import OTPRequest

# وارد کردن سرویس پیامک از اپلیکیشن sms_module
from sms_module.services import SMSManagerService

logger = logging.getLogger(__name__)


class OTPAuthService:
    """
    سرویس مدیریت کدهای یک‌بار مصرف (تولید، اعتبارسنجی و امنیت)
    """

    # تنظیمات امنیتی سیستم
    OTP_LENGTH = 5  # طول کد پیامک (۵ رقمی)
    COOLDOWN_SECONDS = 120  # کاربر تا ۲ دقیقه نمی‌تواند درخواست مجدد بدهد
    MAX_HOURLY_ATTEMPTS = 5  # حداکثر درخواست کد در هر ساعت

    @classmethod
    def _generate_secure_code(cls) -> str:
        """
        تولید کد تصادفی امن (از نظر رمزنگاری غیرقابل پیش‌بینی)
        """
        alphabet = string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(cls.OTP_LENGTH))

    @classmethod
    def request_otp(cls, phone_number: str, purpose: str, ip_address: str = None, user_agent: str = '') -> dict:
        """
        درخواست صدور و ارسال کد پیامکی جدید

        ورودی:
            phone_number: شماره موبایل کاربر (فرمت 09xxxxxxxxx)
            purpose: هدف از ارسال (LOGIN, CHANGE_PHONE, etc.)
            ip_address: آی‌پی درخواست‌دهنده (برای لاگ امنیتی)
            user_agent: مشخصات مرورگر/دستگاه

        خروجی:
            dict با کلیدهای:
                - success: bool (موفقیت‌آمیز بودن عملیات)
                - message: str (پیام برای کاربر)
        """
        now = timezone.now()

        # ==========================================
        # ۱. بررسی Cooldown (آیا در ۲ دقیقه گذشته کدی گرفته است؟)
        # ==========================================
        cooldown_time = now - timedelta(seconds=cls.COOLDOWN_SECONDS)
        recent_otp = OTPRequest.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            created_at__gte=cooldown_time
        ).exists()

        if recent_otp:
            # محاسبه زمان باقیمانده
            latest_otp = OTPRequest.objects.filter(
                phone_number=phone_number,
                purpose=purpose,
                created_at__gte=cooldown_time
            ).order_by('-created_at').first()

            remaining_seconds = int(
                (latest_otp.created_at + timedelta(seconds=cls.COOLDOWN_SECONDS) - now).total_seconds())
            remaining_minutes = remaining_seconds // 60
            remaining_secs = remaining_seconds % 60

            return {
                "success": False,
                "message": f"لطفاً {remaining_minutes} دقیقه و {remaining_secs} ثانیه دیگر تلاش کنید."
            }

        # ==========================================
        # ۲. بررسی Rate Limit (آیا در یک ساعت گذشته بیش از ۵ بار درخواست داده؟)
        # ==========================================
        hourly_time = now - timedelta(hours=1)
        hourly_requests = OTPRequest.objects.filter(
            phone_number=phone_number,
            created_at__gte=hourly_time
        ).count()

        if hourly_requests >= cls.MAX_HOURLY_ATTEMPTS:
            logger.warning(f"Spam detected for phone {phone_number} from IP {ip_address}")
            return {
                "success": False,
                "message": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً یک ساعت دیگر تلاش کنید."
            }

        # ==========================================
        # ۳. تولید کد امن و ثبت در دیتابیس
        # ==========================================
        otp_code = cls._generate_secure_code()

        otp_record = OTPRequest.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent
        )

        logger.info(f"OTP generated for {phone_number}: {otp_code} (Purpose: {purpose})")

        # ==========================================
        # ۴. ارتباط با ماژول SMS Manager برای ارسال پیامک
        # ==========================================
        try:
            sms_service = SMSManagerService()

            # انتخاب قالب بر اساس هدف
            template_name = "OTP_LOGIN" if purpose == OTPRequest.PurposeChoices.LOGIN else "OTP_GENERAL"

            is_sent = sms_service.send_verify(
                mobile=phone_number,
                template_name=template_name,
                parameters={"Code": otp_code}
            )

            if is_sent:
                return {
                    "success": True,
                    "message": "کد تایید با موفقیت ارسال شد."
                }
            else:
                # اگر پیامک نرفت، رکورد دیتابیس را پاک می‌کنیم
                otp_record.delete()
                logger.error(f"Failed to send SMS to {phone_number}")
                return {
                    "success": False,
                    "message": "خطا در ارتباط با سامانه پیامکی. لطفاً دقایقی دیگر تلاش کنید."
                }

        except Exception as e:
            logger.error(f"Error calling SMS service for {phone_number}: {str(e)}")
            otp_record.delete()
            return {
                "success": False,
                "message": "خطای سیستمی رخ داده است. لطفاً بعداً تلاش کنید."
            }

    @classmethod
    def verify_otp(cls, phone_number: str, provided_code: str, purpose: str) -> dict:
        """
        بررسی صحت کد وارد شده توسط کاربر

        ورودی:
            phone_number: شماره موبایل
            provided_code: کد وارد شده توسط کاربر
            purpose: هدف از تایید

        خروجی:
            dict با کلیدهای:
                - success: bool (موفقیت‌آمیز بودن تایید)
                - message: str (پیام برای کاربر)
        """
        # ==========================================
        # ۱. پیدا کردن آخرین کد معتبر برای این شماره
        # ==========================================
        otp_record = OTPRequest.objects.filter(
            phone_number=phone_number,
            purpose=purpose
        ).order_by('-created_at').first()

        if not otp_record:
            return {
                "success": False,
                "message": "هیچ کد تاییدی برای این شماره یافت نشد. لطفاً مجدداً درخواست دهید."
            }

        # ==========================================
        # ۲. بررسی اعتبار کد
        # ==========================================
        if not otp_record.is_valid():
            if otp_record.is_expired:
                return {
                    "success": False,
                    "message": "زمان این کد به پایان رسیده است. لطفاً کد جدیدی درخواست کنید."
                }
            if otp_record.is_blocked:
                return {
                    "success": False,
                    "message": "به دلیل تلاش‌های ناموفق مکرر، این کد مسدود شده است. درخواست جدید ثبت کنید."
                }
            if otp_record.is_used:
                return {
                    "success": False,
                    "message": "این کد قبلاً استفاده شده است. لطفاً کد جدیدی درخواست کنید."
                }

        # ==========================================
        # ۳. بررسی مطابقت کد وارد شده
        # ==========================================
        if otp_record.otp_code != provided_code:
            # افزایش تعداد تلاش‌های ناموفق
            otp_record.failed_attempts += 1
            otp_record.save()

            remained_attempts = 3 - otp_record.failed_attempts

            logger.warning(
                f"Invalid OTP attempt for {phone_number}. "
                f"Failed attempts: {otp_record.failed_attempts}/3"
            )

            if remained_attempts > 0:
                return {
                    "success": False,
                    "message": f"کد وارد شده اشتباه است. ({remained_attempts} تلاش باقیمانده)"
                }
            else:
                return {
                    "success": False,
                    "message": "کد شما به دلیل تلاش‌های ناموفق مسدود شد. لطفاً درخواست جدید ثبت کنید."
                }

        # ==========================================
        # ۴. ✅ کد صحیح است - مارک کردن به عنوان "استفاده شده"
        # ==========================================
        otp_record.is_used = True
        otp_record.save()

        logger.info(f"OTP verified successfully for {phone_number} (Purpose: {purpose})")

        return {
            "success": True,
            "message": "شماره موبایل با موفقیت تایید شد."
        }

    @classmethod
    def cleanup_expired_otps(cls):
        """
        پاک کردن کدهای منقضی شده از دیتابیس (برای بهینه‌سازی)
        این متد را می‌توانید در یک Celery Task یا management command اجرا کنید
        """
        now = timezone.now()
        deleted_count, _ = OTPRequest.objects.filter(expires_at__lt=now).delete()
        logger.info(f"Cleaned up {deleted_count} expired OTP records")
        return deleted_count