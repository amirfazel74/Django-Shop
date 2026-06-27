"""
تست‌های home_module
Tests for home_module
"""
from django.test import TestCase, Client
from django.urls import reverse
from product_module.models import Product, ProductCategory, ProductBrand
from site_module.models import SiteSetting, Slider
import logging

logger = logging.getLogger('home_module')


class HomeViewTestCase(TestCase):
    """تست‌های نمای صفحه اصلی"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        
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
        
        # ایجاد دسته‌بندی
        self.category = ProductCategory.objects.create(
            title='مواد شیمیایی',
            url_title='mavaad-shimi',
            is_active=True,
            is_delete=False,
            show_in_home=True
        )
        
        # ایجاد محصول‌ها
        for i in range(3):
            product = Product.objects.create(
                title=f'محصول {i}',
                slug=f'product-{i}',
                price=10000 + (i * 5000),
                inventory=50 + i,
                weight_value=100 + i,
                weight_unit='g',
                is_active=True,
                is_delete=False
            )
            product.category.add(self.category)
        
        logger.info('تنظیم تست‌های صفحه اصلی')
    
    def test_home_page_status_code(self):
        """آزمایش کد وضعیت صفحه اصلی"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش کد وضعیت صفحه اصلی موفق')
    
    def test_home_page_template(self):
        """آزمایش الگو صفحه اصلی"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home_module/index_page.html')
        logger.info('✓ آزمایش الگو صفحه اصلی موفق')
    
    def test_latest_products_in_context(self):
        """آزمایش وجود محصولات جدید در متن"""
        response = self.client.get('/')
        self.assertIn('latest_products', response.context)
        logger.info('✓ آزمایش محصولات جدید موفق')
    
    def test_most_visit_products_in_context(self):
        """آزمایش وجود محصولات پربازدید در متن"""
        response = self.client.get('/')
        self.assertIn('most_visit_products', response.context)
        logger.info('✓ آزمایش محصولات پربازدید موفق')
    
    def test_categories_in_context(self):
        """آزمایش وجود دسته‌بندی‌ها در متن"""
        response = self.client.get('/')
        self.assertIn('categories_products', response.context)
        logger.info('✓ آزمایش دسته‌بندی‌ها موفق')


class AboutViewTestCase(TestCase):
    """تست‌های نمای درباره"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        self.site_setting = SiteSetting.objects.create(
            site_name='درباره ما',
            site_url='test.example.com',
            address='تهران',
            email='test@example.com',
            copy_right='تمام حقوق',
            about_us_text='متن درباره ما',
            is_main_setting=True
        )
        logger.info('تنظیم تست‌های صفحه درباره')
    
    def test_about_page_status_code(self):
        """آزمایش کد وضعیت صفحه درباره"""
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش کد وضعیت صفحه درباره موفق')
