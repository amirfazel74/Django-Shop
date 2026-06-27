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


class HomePageSection(models.Model):
    class SectionType(models.TextChoices):
        CATEGORIES = 'categories', 'دسته بندی های صفحه اصلی'
        LATEST_PRODUCTS = 'latest_products', 'محصولات جدید'
        PROMO_BANNER = 'promo_banner', 'بنر تبلیغاتی میانی'
        LATEST_ARTICLES = 'latest_articles', 'مقالات جدید'

    section_type = models.CharField(
        max_length=50,
        choices=SectionType.choices,
        unique=True,
        verbose_name='بخش صفحه اصلی'
    )
    title = models.CharField(max_length=250, verbose_name='عنوان')
    subtitle = models.CharField(max_length=500, blank=True, verbose_name='زیرعنوان')
    content = models.TextField(blank=True, verbose_name='متن توضیحی')
    link_text = models.CharField(max_length=100, blank=True, verbose_name='متن لینک یا دکمه')
    link_url = models.CharField(max_length=500, blank=True, verbose_name='آدرس لینک')
    image = models.ImageField(upload_to='home-sections/', blank=True, null=True, verbose_name='تصویر بخش')
    background_color = models.CharField(max_length=20, default='#10b981', verbose_name='رنگ پس زمینه')
    text_color = models.CharField(max_length=20, default='#ffffff', verbose_name='رنگ متن')
    item_limit = models.PositiveSmallIntegerField(default=8, verbose_name='تعداد آیتم قابل نمایش')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال باشد؟')

    class Meta:
        verbose_name = 'بخش صفحه اصلی'
        verbose_name_plural = 'بخش های صفحه اصلی'
        ordering = ['order', 'id']

    def __str__(self):
        return self.get_section_type_display()

# Create your models here.
