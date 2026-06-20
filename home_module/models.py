# models.py در اپلیکیشن مربوطه (مثلاً home_module یا pages)
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class Slider(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان اصلی")
    badge_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="متن تگ (مثلاً: تخفیف‌های بهاره)")

    # استفاده از CKEditor5 برای توضیحات با تنظیمات default شما
    description = CKEditor5Field(verbose_name="توضیحات", config_name='default')

    image = models.ImageField(upload_to='sliders/', verbose_name="تصویر اسلایدر")

    # تنظیمات دکمه اول (اصلی)
    btn1_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="متن دکمه اول")
    btn1_link = models.URLField(blank=True, null=True, verbose_name="لینک دکمه اول")

    # تنظیمات دکمه دوم (فرعی)
    btn2_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="متن دکمه دوم")
    btn2_link = models.URLField(blank=True, null=True, verbose_name="لینک دکمه دوم")

    is_active = models.BooleanField(default=True, verbose_name="فعال است؟")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدرها"
        ordering = ['order', '-id']

    def __str__(self):
        return self.title


from django.db import models

# Create your models here.
