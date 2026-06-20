from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


# ====================================================================
# مدل تماس با ما (بدون تغییر)
# ====================================================================
class ContactUs(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان')
    email = models.EmailField(max_length=300, verbose_name='ایمیل')
    full_name = models.CharField(max_length=300, verbose_name='نام و نام خانوادگی')
    message = models.TextField(verbose_name='متن تماس با ما')
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    response = models.TextField(verbose_name='متن پاسخ تماس با ما', null=True, blank=True)
    is_read_by_admin = models.BooleanField(verbose_name='خوانده شده توسط ادمین', default=False)

    class Meta:
        verbose_name = 'تماس با ما'
        verbose_name_plural = 'لیست تماس با ما'

    def __str__(self):
        return self.title


# ====================================================================
# پروفایل کاربر (آپدیت شده بر اساس فرم سفارش)
# ====================================================================
class UserProfile(models.Model):
    # اتصال به کاربر با روش استاندارد و امن جنگو
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # <--- اینجا تغییر کرد
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='کاربر'
    )

    image = models.ImageField(upload_to='images/profiles', null=True, blank=True, verbose_name='عکس پروفایل')
    # --- اطلاعات گیرنده و آدرس (تمامی فیلدها اختیاری تنظیم شده‌اند) ---
    receiver_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='نام و نام خانوادگی گیرنده')
    receiver_mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره موبایل گیرنده')
    province = models.CharField(max_length=100, null=True, blank=True, verbose_name='استان')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='شهر')
    address = models.TextField(null=True, blank=True, verbose_name='آدرس دقیق', help_text='خیابان، کوچه، پلاک، زنگ...')
    postal_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد پستی (۱۰ رقمی)')

    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'

    def __str__(self):
        return f"پروفایل {self.user.username}"


# ====================================================================
# ساخت اتوماتیک پروفایل هنگام ثبت‌نام
# ====================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
