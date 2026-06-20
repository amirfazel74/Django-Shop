from django.db import models
from account_module.models import User
from product_module.models import Product


# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    is_paid = models.BooleanField(verbose_name='نهایی شده/نشده', default=False)
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    
    # Status
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
        ('canceled', 'لغو شده'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت سفارش')
    
    # Zibal Payment Data
    payment_track_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='شناسه پرداخت زیبال (trackId)')
    payment_ref_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='شماره پیگیری پرداخت (refNumber)')
    
    # Shipping Info
    SHIPPING_CHOICES = (
        ('post', 'پست پیشتاز'),
        ('barbari', 'ارسال با باربری (پس‌کرایه)'),
    )
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, null=True, blank=True, verbose_name='روش ارسال')
    shipping_cost = models.IntegerField(default=0, verbose_name='هزینه ارسال')
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='کد رهگیری ارسال')
    
    # Address Info (Snapshotted at checkout)
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='نام گیرنده')
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='نام خانوادگی گیرنده')
    mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name='شماره موبایل گیرنده')
    province = models.CharField(max_length=100, null=True, blank=True, verbose_name='استان')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='شهر')
    address = models.TextField(null=True, blank=True, verbose_name='آدرس دقیق')
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='کد پستی')

    def __str__(self):
        return str(self.user)

    def calculate_total_price(self):
        total_amount = 0
        if self.is_paid:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.final_price * order_detail.count
        else:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.product.price * order_detail.count

        return total_amount

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید کاربران'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='سبد خرید')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    final_price = models.IntegerField(null=True, blank=True, verbose_name='قیمت نهایی تکی محصول')
    count = models.IntegerField(verbose_name='تعداد')

    def get_total_price(self):
        return self.count * self.product.price

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name = 'جزییات سبد خرید'
        verbose_name_plural = 'لیست جزییات سبدهای خرید'
