"""
تست‌های order_module
Tests for order_module
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from order_module.models import Order, OrderDetail
from product_module.models import Product, ProductCategory, ProductBrand
import logging

User = get_user_model()
logger = logging.getLogger('order_module')


class OrderModelTestCase(TestCase):
    """تست‌های مدل Order"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.user = User.objects.create_user(
            username='orderuser',
            email='order@example.com',
            password='pass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            is_paid=False,
            status='pending',
            shipping_cost=85000
        )
        logger.info(f'ایجاد سفارش برای کاربر: {self.user.username}')
    
    def test_order_creation(self):
        """آزمایش ایجاد سفارش"""
        self.assertEqual(self.order.user, self.user)
        self.assertFalse(self.order.is_paid)
        self.assertEqual(self.order.status, 'pending')
        logger.info('✓ آزمایش ایجاد سفارش موفق')
    
    def test_order_status_choices(self):
        """آزمایش گزینه‌های وضعیت سفارش"""
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'canceled']
        for status in valid_statuses:
            order = Order.objects.create(user=self.user, status=status)
            self.assertEqual(order.status, status)
        logger.info('✓ آزمایش گزینه‌های وضعیت سفارش موفق')
    
    def test_order_shipping_cost(self):
        """آزمایش هزینه ارسال"""
        self.assertEqual(self.order.shipping_cost, 85000)
        logger.info('✓ آزمایش هزینه ارسال موفق')
    
    def test_order_payment_info(self):
        """آزمایش اطلاعات پرداخت"""
        self.order.payment_track_id = 'track123'
        self.order.payment_ref_number = 'ref123'
        self.order.save()
        self.assertEqual(self.order.payment_track_id, 'track123')
        self.assertEqual(self.order.payment_ref_number, 'ref123')
        logger.info('✓ آزمایش اطلاعات پرداخت موفق')
    
    def test_order_shipping_address(self):
        """آزمایش آدرس ارسال"""
        self.order.first_name = 'احمد'
        self.order.last_name = 'محمودی'
        self.order.mobile = '09123456789'
        self.order.province = 'تهران'
        self.order.city = 'تهران'
        self.order.address = 'خیابان انقلاب، پلاک 123'
        self.order.postal_code = '1234567890'
        self.order.save()
        
        self.assertEqual(self.order.first_name, 'احمد')
        self.assertEqual(self.order.province, 'تهران')
        logger.info('✓ آزمایش آدرس ارسال موفق')
    
    def test_order_str(self):
        """آزمایش نمایش متنی سفارش"""
        self.assertEqual(str(self.order), str(self.user))
        logger.info('✓ آزمایش نمایش متنی سفارش موفق')


class OrderDetailTestCase(TestCase):
    """تست‌های مدل OrderDetail"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.user = User.objects.create_user(
            username='orderuser',
            password='pass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            is_paid=False
        )
        
        # ایجاد محصول
        category = ProductCategory.objects.create(
            title='دسته‌بندی',
            url_title='cat',
            is_active=True,
            is_delete=False
        )
        self.product = Product.objects.create(
            title='محصول',
            slug='product',
            price=10000,
            inventory=100,
            weight_value=500,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        self.product.category.add(category)
        
        self.order_detail = OrderDetail.objects.create(
            order=self.order,
            product=self.product,
            count=2
        )
        logger.info('تنظیم جزئیات سفارش')
    
    def test_order_detail_creation(self):
        """آزمایش ایجاد جزئیات سفارش"""
        self.assertEqual(self.order_detail.order, self.order)
        self.assertEqual(self.order_detail.product, self.product)
        self.assertEqual(self.order_detail.count, 2)
        logger.info('✓ آزمایش ایجاد جزئیات سفارش موفق')
    
    def test_order_detail_get_total_price(self):
        """آزمایش محاسبه قیمت کل"""
        total = self.order_detail.get_total_price()
        expected = 2 * 10000
        self.assertEqual(total, expected)
        logger.info('✓ آزمایش محاسبه قیمت کل موفق')
    
    def test_order_detail_final_price(self):
        """آزمایش قیمت نهایی"""
        self.order_detail.final_price = 9000  # قیمت با تخفیف
        self.order_detail.save()
        self.assertEqual(self.order_detail.final_price, 9000)
        logger.info('✓ آزمایش قیمت نهایی موفق')
    
    def test_order_detail_str(self):
        """آزمایش نمایش متنی جزئیات سفارش"""
        self.assertEqual(str(self.order_detail), str(self.order))
        logger.info('✓ آزمایش نمایش متنی جزئیات سفارش موفق')


class OrderCalculationTestCase(TestCase):
    """تست‌های محاسبات سفارش"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.user = User.objects.create_user(
            username='calcuser',
            password='pass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            is_paid=False
        )
        
        category = ProductCategory.objects.create(
            title='دسته‌بندی',
            url_title='cat',
            is_active=True,
            is_delete=False
        )
        
        # ایجاد محصولات
        self.product1 = Product.objects.create(
            title='محصول 1',
            slug='product-1',
            price=10000,
            inventory=100,
            weight_value=500,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        self.product1.category.add(category)
        
        self.product2 = Product.objects.create(
            title='محصول 2',
            slug='product-2',
            price=20000,
            inventory=100,
            weight_value=1000,
            weight_unit='g',
            is_active=True,
            is_delete=False
        )
        self.product2.category.add(category)
        
        logger.info('تنظیم محاسبات سفارش')
    
    def test_calculate_total_price_unpaid(self):
        """آزمایش محاسبه قیمت کل برای سفارش نپرداخت شده"""
        OrderDetail.objects.create(
            order=self.order,
            product=self.product1,
            count=2
        )
        OrderDetail.objects.create(
            order=self.order,
            product=self.product2,
            count=1
        )
        
        total = self.order.calculate_total_price()
        expected = (2 * 10000) + (1 * 20000)
        self.assertEqual(total, expected)
        logger.info('✓ آزمایش محاسبه قیمت برای سفارش نپرداخت شده موفق')
    
    def test_calculate_total_price_paid(self):
        """آزمایش محاسبه قیمت کل برای سفارش پرداخت شده"""
        detail1 = OrderDetail.objects.create(
            order=self.order,
            product=self.product1,
            count=2,
            final_price=9000  # قیمت با تخفیف
        )
        detail2 = OrderDetail.objects.create(
            order=self.order,
            product=self.product2,
            count=1,
            final_price=18000  # قیمت با تخفیف
        )
        
        self.order.is_paid = True
        self.order.save()
        
        total = self.order.calculate_total_price()
        expected = (2 * 9000) + (1 * 18000)
        self.assertEqual(total, expected)
        logger.info('✓ آزمایش محاسبه قیمت برای سفارش پرداخت شده موفق')
    
    def test_empty_order_total(self):
        """آزمایش محاسبه برای سفارش خالی"""
        total = self.order.calculate_total_price()
        self.assertEqual(total, 0)
        logger.info('✓ آزمایش محاسبه برای سفارش خالی موفق')


class OrderQueryTestCase(TestCase):
    """تست‌های جستجوی سفارش"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
        # ایجاد سفارش‌ها
        self.order1 = Order.objects.create(user=self.user1, status='pending')
        self.order2 = Order.objects.create(user=self.user1, status='processing')
        self.order3 = Order.objects.create(user=self.user2, status='pending')
        
        logger.info('تنظیم جستجوی سفارش‌ها')
    
    def test_get_user_orders(self):
        """آزمایش دریافت سفارش‌های کاربر"""
        orders = Order.objects.filter(user=self.user1)
        self.assertEqual(orders.count(), 2)
        logger.info('✓ آزمایش دریافت سفارش‌های کاربر موفق')
    
    def test_filter_by_status(self):
        """آزمایش فیلتر براساس وضعیت"""
        pending_orders = Order.objects.filter(status='pending')
        self.assertEqual(pending_orders.count(), 2)
        logger.info('✓ آزمایش فیلتر براساس وضعیت موفق')
    
    def test_filter_unpaid_orders(self):
        """آزمایش فیلتر سفارش‌های نپرداخت شده"""
        unpaid = Order.objects.filter(is_paid=False)
        self.assertEqual(unpaid.count(), 3)
        logger.info('✓ آزمایش فیلتر سفارش‌های نپرداخت شده موفق')
    
    def test_filter_paid_orders(self):
        """آزمایش فیلتر سفارش‌های پرداخت شده"""
        self.order1.is_paid = True
        self.order1.save()
        paid = Order.objects.filter(is_paid=True)
        self.assertEqual(paid.count(), 1)
        logger.info('✓ آزمایش فیلتر سفارش‌های پرداخت شده موفق')
