from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django_ckeditor_5.fields import CKEditor5Field
from account_module.models import User


class HazardClass(models.TextChoices):
    DANGER_RED = 'red', 'بسیار خطرناک (نوار قرمز)'
    DANGER_YELLOW = 'yellow', 'خطرناک (نوار زرد)'
    DANGER_BLUE = 'blue', 'خطر متوسط (نوار آبی)'
    SAFE_GREEN = 'green', 'کم خطر (نوار سبز)'


# --- Choices ---
class WeightUnit(models.TextChoices):
    GRAM = 'g', 'گرم'
    KILOGRAM = 'kg', 'کیلوگرم'
    CC = 'cc', 'سی‌سی'
    LITER = 'l', 'لیتر'
    PIECE = 'pcs', 'عدد'


class ShippingClass(models.TextChoices):
    NORMAL_POST = 'post', 'قابل ارسال با پست'
    FREIGHT_ONLY = 'freight', 'فقط ارسال با باربری (حجم بالا / خطرناک)'


class ProductCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان در url')

    # --- فیلدهای جدید ---
    image = models.ImageField(upload_to='images/categories', null=True, blank=True, verbose_name='تصویر دسته‌بندی')
    color = models.CharField(max_length=20, default='#2563eb', verbose_name='رنگ پس‌زمینه (کد هگز)',
                             help_text='مثال: #2563eb (آبی) یا #10b981 (سبز)')
    show_in_home = models.BooleanField(default=False, verbose_name='نمایش در صفحه اصلی',
                                       help_text='اگر فعال باشد، این دسته‌بندی در صفحه اصلی نمایش داده می‌شود')
    # -------------------

    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'


class ProductBrand(models.Model):
    title = models.CharField(max_length=300, verbose_name='نام برند', db_index=True)
    url_title = models.CharField(max_length=300, verbose_name='نام در url', db_index=True)
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'

    def __str__(self):
        return self.title


class Product(models.Model):
    # 1. اطلاعات پایه و عمومی
    title = models.CharField(max_length=300, verbose_name='نام محصول')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=200, unique=True,
                            verbose_name='عنوان در url')
    category = models.ManyToManyField(ProductCategory, related_name='product_categories', verbose_name='دسته‌بندی‌ها')
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, verbose_name='برند', null=True, blank=True)
    image = models.ImageField(upload_to='images/products', null=True, blank=True, verbose_name='تصویر اصلی محصول')

    # 2. مالی، موجودی و فیزیک کالا
    price = models.IntegerField(verbose_name='قیمت (تومان)')
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار (تعداد)')
    weight_value = models.FloatField(verbose_name='مقدار وزن/حجم', help_text="مثال: 1.5 یا 500")
    weight_unit = models.CharField(max_length=10, choices=WeightUnit.choices, default=WeightUnit.LITER,
                                   verbose_name='واحد اندازه گیری')
    hazard_class = models.CharField(max_length=20, choices=HazardClass.choices, null=True, blank=True,
                                    verbose_name='کلاس خطر سموم')
    is_wholesale = models.BooleanField(default=False, verbose_name='فروش عمده (همکار/کشاورز)',
                                       help_text='با فعال کردن این گزینه، تگ آبی رنگ "عمده" روی محصول نمایش داده می‌شود.')
    discount_percent = models.PositiveIntegerField(default=0, verbose_name='درصد تخفیف',
                                                   help_text='برای نمایش تگ قرمز رنگ درصد تخفیف')
    # 3. لاجستیک و ارسال
    shipping_class = models.CharField(max_length=20, choices=ShippingClass.choices, default=ShippingClass.NORMAL_POST,
                                      verbose_name='کلاس ارسال')
    max_postal_qty = models.PositiveIntegerField(default=5, verbose_name='حداکثر تعداد مجاز برای پست',
                                                 help_text="اگر کاربر بیشتر از این تعداد سفارش داد، کل سبد به اجبار با باربری ارسال می‌شود.")

    # 4. محتوا و توضیحات
    short_description = models.CharField(max_length=360, db_index=True, null=True,
                                         verbose_name='توضیحات کوتاه (کارت محصول)')
    description = CKEditor5Field(verbose_name='توضیحات اصلی و معرفی', config_name='default')
    technical_description = CKEditor5Field(verbose_name='توضیحات فنی', config_name='default', null=True, blank=True)

    # ==========================================
    # 5. فیلدهای تخصصی اگری-تک (سم، کود، بذر)
    # ==========================================
    active_ingredient = models.CharField(max_length=250, null=True, blank=True, verbose_name='ماده موثره (فرمولاسیون)')
    phi_days = models.PositiveIntegerField(null=True, blank=True, verbose_name='دوره کارنس (روز)',
                                           help_text="تعداد روزهای ماندگاری سم تا زمان برداشت")
    msds_file = models.FileField(upload_to='msds_files/', null=True, blank=True,
                                 validators=[FileExtensionValidator(['pdf'])], verbose_name='فایل اطلاعات ایمنی (MSDS)')
    usage_timing = models.TextField(null=True, blank=True, verbose_name='نحوه و بهترین زمان مصرف')

    # داده‌های لازم برای ماشین‌حساب (بر حسب لیتر/کیلو در هر هکتار - 10,000 متر)
    # این اعداد در فرانت‌اند به جاوااسکریپت پاس داده میشن تا ضرب و تقسیم بشن
    dosage_greenhouse = models.FloatField(null=True, blank=True, verbose_name='دوز مصرف گلخانه (در هکتار)')
    dosage_orchard = models.FloatField(null=True, blank=True, verbose_name='دوز مصرف باغات (در هکتار)')
    dosage_farm = models.FloatField(null=True, blank=True, verbose_name='دوز مصرف زراعت (در هکتار)')

    # 6. کراس‌سلینگ (محصولات مکمل)
    complementary_safety_gears = models.ManyToManyField('self', blank=True, symmetrical=False,
                                                        verbose_name='تجهیزات ایمنی/مکمل پیشنهادی')

    # 7. وضعیت
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده / نشده')

    def get_absolute_url(self):
        return reverse('product-detail', args=[self.slug])

    def __str__(self):
        return f"{self.title} ({self.price})"

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'


class ProductTag(models.Model):
    caption = models.CharField(max_length=300, db_index=True, verbose_name='عنوان تگ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_tags')

    class Meta:
        verbose_name = 'تگ محصول'
        verbose_name_plural = 'تگ‌های محصولات'

    def __str__(self):
        return self.caption


# مدل‌های بازدید و گالری بدون تغییر می‌مانند
class ProductVisit(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='محصول')
    ip = models.CharField(max_length=30, verbose_name='آی‌پی کاربر')
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='کاربر', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.title} / {self.ip}'

    class Meta:
        verbose_name = 'بازدید محصول'
        verbose_name_plural = 'بازدیدهای محصول'


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    image = models.ImageField(upload_to='images/product-gallery', verbose_name='تصویر')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'تصویر گالری'
        verbose_name_plural = 'گالری تصاویر'
