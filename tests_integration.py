"""
تست‌های یکپارچگی (Integration Tests)
Integration tests for the entire e-shop system
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from product_module.models import Product, ProductCategory, ProductBrand
from order_module.models import Order, OrderDetail
from site_module.models import SiteSetting
import logging

User = get_user_model()
logger = logging.getLogger('eshop')


class UserShoppingJourneyTestCase(TestCase):
    """تست‌های سفر خریداری کاربر"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        
        # ایجاد کاربر
        self.user = User.objects.create_user(
            username='shopper',
            email='shopper@example.com',
            password='pass123',
            first_name='خریدار',
            last_name='تست'
        )
        
        # ایجاد دسته‌بندی
        self.category = ProductCategory.objects.create(
            title='مواد شیمیایی',
            url_title='mavaad-shimi',
            is_active=True,
            is_delete=False,
            show_in_home=True
        )
        
        # ایجاد برند
        self.brand = ProductBrand.objects.create(
            title='برند A',
            url_title='brand-a',
            is_active=True
        )
        
        # ایجاد محصولات
        self.product1 = Product.objects.create(
            title='محصول 1',
            slug='product-1',
            price=50000,
            inventory=100,
            weight_value=500,
            weight_unit='g',
            brand=self.brand,
            is_active=True,
            is_delete=False
        )
        self.product1.category.add(self.category)
        
        self.product2 = Product.objects.create(
            title='محصول 2',
            slug='product-2',
            price=75000,
            inventory=50,
            weight_value=1000,
            weight_unit='g',
            brand=self.brand,
            is_active=True,
            is_delete=False
        )
        self.product2.category.add(self.category)
        
        # ایجاد تنظیمات سایت
        self.site_setting = SiteSetting.objects.create(
            site_name='فروشگاه تست',
            site_url='test.example.com',
            address='تهران',
            email='test@example.com',
            copy_right='تمام حقوق',
            about_us_text='درباره ما',
            is_main_setting=True
        )
        
        logger.info('تنظیم سفر خریداری')
    
    def test_user_can_browse_home_page(self):
        """آزمایش اینکه کاربر می‌تواند صفحه اصلی را مرور کند"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش مرور صفحه اصلی موفق')
    
    def test_user_can_view_products(self):
        """آزمایش اینکه کاربر می‌تواند محصولات را مشاهده کند"""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش مشاهده محصولات موفق')
    
    def test_user_can_login(self):
        """آزمایش اینکه کاربر می‌تواند وارد شود"""
        logged_in = self.client.login(username='shopper', password='pass123')
        self.assertTrue(logged_in)
        logger.info('✓ آزمایش ورود کاربر موفق')
    
    def test_user_can_create_order(self):
        """آزمایش اینکه کاربر می‌تواند سفارش ایجاد کند"""
        self.client.login(username='shopper', password='pass123')
        
        # ایجاد سفارش
        order = Order.objects.create(user=self.user, is_paid=False)
        
        # افزودن محصولات به سفارش
        OrderDetail.objects.create(
            order=order,
            product=self.product1,
            count=2
        )
        OrderDetail.objects.create(
            order=order,
            product=self.product2,
            count=1
        )
        
        # بررسی سفارش
        self.assertEqual(order.orderdetail_set.count(), 2)
        self.assertEqual(order.calculate_total_price(), (2 * 50000) + (1 * 75000))
        logger.info('✓ آزمایش ایجاد سفارش موفق')
    
    def test_user_can_access_user_panel(self):
        """آزمایش اینکه کاربر می‌تواند به پنل کاربری دسترسی داشته باشد"""
        self.client.login(username='shopper', password='pass123')
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش دسترسی به پنل کاربری موفق')


class AdminManagementTestCase(TestCase):
    """تست‌های مدیریت ادمین"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        
        # ایجاد ادمین
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        logger.info('تنظیم مدیریت ادمین')
    
    def test_admin_can_login(self):
        """آزمایش اینکه ادمین می‌تواند وارد شود"""
        logged_in = self.client.login(username='admin', password='adminpass123')
        self.assertTrue(logged_in)
        logger.info('✓ آزمایش ورود ادمین موفق')
    
    def test_admin_can_create_product(self):
        """آزمایش اینکه ادمین می‌تواند محصول ایجاد کند"""
        category = ProductCategory.objects.create(
            title='دسته‌بندی',
            url_title='category',
            is_active=True,
            is_delete=False
        )
        
        product = Product.objects.create(
            title='محصول ادمین',
            slug='admin-product',
            price=100000,
            inventory=200,
            weight_value=2000,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        product.category.add(category)
        
        self.assertEqual(product.title, 'محصول ادمین')
        self.assertEqual(product.price, 100000)
        logger.info('✓ آزمایش ایجاد محصول توسط ادمین موفق')
    
    def test_admin_can_manage_categories(self):
        """آزمایش اینکه ادمین می‌تواند دسته‌بندی‌ها را مدیریت کند"""
        cat1 = ProductCategory.objects.create(
            title='دسته 1',
            url_title='cat-1',
            is_active=True,
            is_delete=False
        )
        cat2 = ProductCategory.objects.create(
            title='دسته 2',
            url_title='cat-2',
            is_active=False,
            is_delete=False
        )
        
        # بروزرسانی
        cat1.title = 'دسته 1 بروزرسانی شده'
        cat1.save()
        
        # بررسی
        self.assertEqual(ProductCategory.objects.count(), 2)
        self.assertEqual(cat1.title, 'دسته 1 بروزرسانی شده')
        logger.info('✓ آزمایش مدیریت دسته‌بندی‌ها موفق')


class OrderProcessingTestCase(TestCase):
    """تست‌های پردازش سفارش"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        # ایجاد کاربر
        self.user = User.objects.create_user(
            username='orderer',
            password='pass123'
        )
        
        # ایجاد دسته‌بندی و محصول
        category = ProductCategory.objects.create(
            title='دسته‌بندی',
            url_title='category',
            is_active=True,
            is_delete=False
        )
        
        self.product = Product.objects.create(
            title='محصول',
            slug='product',
            price=100000,
            inventory=50,
            weight_value=1000,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        self.product.category.add(category)
        
        # ایجاد سفارش
        self.order = Order.objects.create(
            user=self.user,
            is_paid=False,
            status='pending'
        )
        
        logger.info('تنظیم پردازش سفارش')
    
    def test_order_status_progression(self):
        """آزمایش پیشرفت وضعیت سفارش"""
        # pending -> processing
        self.order.status = 'processing'
        self.order.save()
        self.assertEqual(self.order.status, 'processing')
        
        # processing -> shipped
        self.order.status = 'shipped'
        self.order.save()
        self.assertEqual(self.order.status, 'shipped')
        
        # shipped -> delivered
        self.order.status = 'delivered'
        self.order.is_paid = True
        self.order.save()
        self.assertEqual(self.order.status, 'delivered')
        self.assertTrue(self.order.is_paid)
        logger.info('✓ آزمایش پیشرفت وضعیت سفارش موفق')
    
    def test_order_with_shipping_address(self):
        """آزمایش سفارش با آدرس ارسال"""
        self.order.first_name = 'احمد'
        self.order.last_name = 'محمودی'
        self.order.mobile = '09123456789'
        self.order.province = 'تهران'
        self.order.city = 'تهران'
        self.order.address = 'خیابان انقلاب'
        self.order.postal_code = '1234567890'
        self.order.shipping_method = 'post'
        self.order.save()
        
        self.assertEqual(self.order.first_name, 'احمد')
        self.assertEqual(self.order.shipping_method, 'post')
        logger.info('✓ آزمایش سفارش با آدرس ارسال موفق')
    
    def test_order_payment_tracking(self):
        """آزمایش پیگیری پرداخت سفارش"""
        self.order.payment_track_id = 'track123456'
        self.order.payment_ref_number = 'ref789012'
        self.order.is_paid = True
        self.order.status = 'processing'
        self.order.save()
        
        self.assertEqual(self.order.payment_track_id, 'track123456')
        self.assertEqual(self.order.payment_ref_number, 'ref789012')
        self.assertTrue(self.order.is_paid)
        logger.info('✓ آزمایش پیگیری پرداخت موفق')


class DatabaseIntegrityTestCase(TestCase):
    """تست‌های یکپارچگی دیتابیس"""
    
    def test_cascade_delete_category(self):
        """آزمایش حذف متوالی دسته‌بندی"""
        category = ProductCategory.objects.create(
            title='دسته‌بندی حذف',
            url_title='delete-cat',
            is_active=True,
            is_delete=False
        )
        
        product = Product.objects.create(
            title='محصول',
            slug='product',
            price=50000,
            inventory=10,
            weight_value=500,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        product.category.add(category)
        
        # حذف دسته‌بندی نباید محصول را حذف کند
        # چون M2M است، نه FK
        category.delete()
        self.assertTrue(Product.objects.filter(id=product.id).exists())
        logger.info('✓ آزمایش یکپارچگی حذف موفق')
    
    def test_user_order_relationship(self):
        """آزمایش رابطه کاربر و سفارش"""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        order1 = Order.objects.create(user=user)
        order2 = Order.objects.create(user=user)
        
        self.assertEqual(user.order_set.count(), 2)
        logger.info('✓ آزمایش رابطه کاربر و سفارش موفق')
