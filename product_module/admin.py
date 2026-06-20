from django.contrib import admin
from .models import (
    Product, ProductCategory, ProductBrand,
    ProductTag, ProductVisit, ProductGallery
)
from django.utils.html import format_html

# ==========================================
# Inlines (زیرمجموعه‌های داخل صفحه محصول)
# ==========================================
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    max_num = 5  # محدودیت ۵ عکس گالری که قبلاً صحبت کردیم
    verbose_name = 'تصویر گالری'
    verbose_name_plural = 'گالری تصاویر (حداکثر ۵ عکس)'


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1
    verbose_name = 'تگ'
    verbose_name_plural = 'تگ‌های محصول'


# ==========================================
# دسته‌بندی و برند
# ==========================================
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'url_title', 'color_preview', 'is_active', 'is_delete')
    list_filter = ('is_active', 'is_delete')
    search_fields = ('title', 'url_title')
    prepopulated_fields = {'url_title': ('title',)}
    list_editable = ('is_active',)

    # متد برای نمایش پیش‌نمایش رنگ در پنل ادمین
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<span style="display:inline-block; width: 20px; height: 20px; border-radius: 50%; background-color: {}; border: 1px solid #ccc; vertical-align: middle;"></span> <span style="vertical-align: middle; margin-right: 5px; font-size: 12px;">{}</span>',
                obj.color, obj.color
            )
        return '-'
    color_preview.short_description = 'رنگ اختصاصی'

@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'url_title', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'url_title')
    prepopulated_fields = {'url_title': ('title',)}
    list_editable = ('is_active',)


# ==========================================
# محصول اصلی (هسته مرکزی داشبورد)
# ==========================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # تنظیمات نمای لیست محصولات
    list_display = ('title', 'brand', 'price', 'inventory', 'shipping_class', 'is_active')
    list_editable = ('price', 'inventory', 'is_active')  # ویرایش سریع از همان صفحه لیست
    list_filter = ('category', 'brand', 'shipping_class', 'is_active', 'is_delete')
    search_fields = ('title', 'active_ingredient', 'short_description')
    prepopulated_fields = {'slug': ('title',)}

    # ویجت‌های زیباتر برای انتخاب چندگانه (باکس‌های دو طرفه)
    filter_horizontal = ('category', 'complementary_safety_gears')

    # اضافه کردن گالری و تگ‌ها به انتهای صفحه ویرایش محصول
    inlines = [ProductGalleryInline, ProductTagInline]

    # گروه‌بندی بسیار زیبای فیلدها در صفحه ایجاد/ویرایش محصول
    fieldsets = (
        ('۱. اطلاعات پایه و عمومی', {
            'fields': (
                ('title', 'slug'),
                ('brand', 'image'),
                'category'
            )
        }),
        ('۲. مالی، موجودی و فیزیک کالا', {
            'fields': (
                ('price', 'inventory'),
                ('weight_value', 'weight_unit')
            )
        }),
        ('۳. لاجستیک و ارسال', {
            'fields': (
                'shipping_class',
                'max_postal_qty'
            ),
            'description': 'تنظیمات مربوط به نحوه ارسال مرسوله با پست یا باربری.'
        }),
        ('۴. محتوا و توضیحات', {
            'fields': (
                'short_description',
                'description',
                'technical_description'
            )
        }),
        ('۵. اطلاعات تخصصی اگری-تک', {
            'classes': ('collapse',),  # این بخش به صورت کشویی (بسته) باز می‌شود تا صفحه شلوغ نشود
            'fields': (
                ('active_ingredient', 'phi_days'),
                'usage_timing',
                'msds_file'
            )
        }),
        ('۶. متغیرهای ماشین‌حساب (دوز مصرف)', {
            'classes': ('collapse',),  # به صورت کشویی
            'fields': (
                ('dosage_greenhouse', 'dosage_orchard', 'dosage_farm'),
            ),
            'description': 'اعداد را بر اساس مقدار مصرف در "هکتار" (۱۰,۰۰۰ متر مربع) وارد کنید.'
        }),
        ('۷. کراس‌سلینگ (محصولات مکمل)', {
            'fields': ('complementary_safety_gears',),
            'description': 'محصولات ایمنی مثل دستکش و ماسک یا کودهای مکمل را انتخاب کنید.'
        }),
        ('۸. وضعیت', {
            'fields': (('is_active', 'is_delete'),)
        }),
    )


# ==========================================
# بازدیدهای محصول
# ==========================================
@admin.register(ProductVisit)
class ProductVisitAdmin(admin.ModelAdmin):
    list_display = ('product', 'ip', 'user')
    list_filter = ('product',)
    search_fields = ('ip', 'product__title', 'user__username')
    # بازدیدها معمولاً فقط برای خواندن هستند و نباید ویرایش شوند
    readonly_fields = ('product', 'ip', 'user')

    # برای جلوگیری از اضافه کردن دستی بازدید توسط ادمین
    def has_add_permission(self, request):
        return False
