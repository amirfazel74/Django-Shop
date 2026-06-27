"""
تست‌های product_module
Tests for product_module
"""
from django.test import TestCase
from product_module.models import Product, ProductCategory, ProductBrand
import logging

logger = logging.getLogger('product_module')


class ProductCategoryTestCase(TestCase):
    """تست‌های دسته‌بندی محصولات"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.category = ProductCategory.objects.create(
            title='مواد شیمیایی',
            url_title='mavaad-shimi',
            is_active=True,
            is_delete=False,
            color='#2563eb',
            show_in_home=True
        )
        logger.info(f'ایجاد دسته‌بندی: {self.category.title}')
    
    def test_category_creation(self):
        """آزمایش ایجاد دسته‌بندی"""
        self.assertEqual(self.category.title, 'مواد شیمیایی')
        self.assertTrue(self.category.is_active)
        self.assertFalse(self.category.is_delete)
        logger.info('✓ آزمایش ایجاد دسته‌بندی موفق')
    
    def test_category_str(self):
        """آزمایش نمایش متنی دسته‌بندی"""
        self.assertEqual(str(self.category), 'مواد شیمیایی')
        logger.info('✓ آزمایش نمایش متنی دسته‌بندی موفق')
    
    def test_category_color(self):
        """آزمایش رنگ دسته‌بندی"""
        self.assertEqual(self.category.color, '#2563eb')
        logger.info('✓ آزمایش رنگ دسته‌بندی موفق')
    
    def test_category_show_in_home(self):
        """آزمایش نمایش در صفحه اصلی"""
        self.assertTrue(self.category.show_in_home)
        logger.info('✓ آزمایش نمایش در صفحه اصلی موفق')
    
    def test_inactive_category(self):
        """آزمایش دسته‌بندی غیرفعال"""
        inactive_cat = ProductCategory.objects.create(
            title='دسته‌بندی غیرفعال',
            url_title='inactive',
            is_active=False,
            is_delete=False
        )
        self.assertFalse(inactive_cat.is_active)
        logger.info('✓ آزمایش دسته‌بندی غیرفعال موفق')


class ProductBrandTestCase(TestCase):
    """تست‌های برند محصولات"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.brand = ProductBrand.objects.create(
            title='برند تست',
            url_title='brand-test',
            is_active=True
        )
        logger.info(f'ایجاد برند: {self.brand.title}')
    
    def test_brand_creation(self):
        """آزمایش ایجاد برند"""
        self.assertEqual(self.brand.title, 'برند تست')
        self.assertTrue(self.brand.is_active)
        logger.info('✓ آزمایش ایجاد برند موفق')
    
    def test_brand_str(self):
        """آزمایش نمایش متنی برند"""
        self.assertEqual(str(self.brand), 'برند تست')
        logger.info('✓ آزمایش نمایش متنی برند موفق')
    
    def test_brand_url_title(self):
        """آزمایش عنوان URL برند"""
        self.assertEqual(self.brand.url_title, 'brand-test')
        logger.info('✓ آزمایش عنوان URL برند موفق')


class ProductTestCase(TestCase):
    """تست‌های محصول"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.category = ProductCategory.objects.create(
            title='مواد شیمیایی',
            url_title='mavaad-shimi',
            is_active=True,
            is_delete=False
        )
        self.brand = ProductBrand.objects.create(
            title='برند A',
            url_title='brand-a',
            is_active=True
        )
        self.product = Product.objects.create(
            title='محصول تست',
            slug='product-test',
            price=50000,
            inventory=100,
            weight_value=500,
            weight_unit='g',
            hazard_class='green',
            shipping_class='post',
            brand=self.brand,
            is_active=True,
            is_delete=False
        )
        self.product.category.add(self.category)
        logger.info(f'ایجاد محصول: {self.product.title}')
    
    def test_product_creation(self):
        """آزمایش ایجاد محصول"""
        self.assertEqual(self.product.title, 'محصول تست')
        self.assertEqual(self.product.price, 50000)
        self.assertEqual(self.product.inventory, 100)
        logger.info('✓ آزمایش ایجاد محصول موفق')
    
    def test_product_slug(self):
        """آزمایش slug محصول"""
        self.assertEqual(self.product.slug, 'product-test')
        logger.info('✓ آزمایش slug محصول موفق')
    
    def test_product_weight(self):
        """آزمایش وزن محصول"""
        self.assertEqual(self.product.weight_value, 500)
        self.assertEqual(self.product.weight_unit, 'g')
        logger.info('✓ آزمایش وزن محصول موفق')
    
    def test_product_hazard_class(self):
        """آزمایش کلاس خطر محصول"""
        self.assertEqual(self.product.hazard_class, 'green')
        logger.info('✓ آزمایش کلاس خطر محصول موفق')
    
    def test_product_category_relationship(self):
        """آزمایش رابطه محصول و دسته‌بندی"""
        categories = self.product.category.all()
        self.assertEqual(categories.count(), 1)
        self.assertIn(self.category, categories)
        logger.info('✓ آزمایش رابطه محصول و دسته‌بندی موفق')
    
    def test_product_brand_relationship(self):
        """آزمایش رابطه محصول و برند"""
        self.assertEqual(self.product.brand, self.brand)
        logger.info('✓ آزمایش رابطه محصول و برند موفق')
    
    def test_product_status(self):
        """آزمایش وضعیت محصول"""
        self.assertTrue(self.product.is_active)
        self.assertFalse(self.product.is_delete)
        logger.info('✓ آزمایش وضعیت محصول موفق')
    
    def test_product_multiple_categories(self):
        """آزمایش محصول با چندین دسته‌بندی"""
        cat2 = ProductCategory.objects.create(
            title='دسته‌بندی دوم',
            url_title='cat-2',
            is_active=True,
            is_delete=False
        )
        self.product.category.add(cat2)
        self.assertEqual(self.product.category.count(), 2)
        logger.info('✓ آزمایش محصول با چندین دسته‌بندی موفق')
    
    def test_product_inactive(self):
        """آزمایش محصول غیرفعال"""
        self.product.is_active = False
        self.product.save()
        self.assertFalse(self.product.is_active)
        logger.info('✓ آزمایش محصول غیرفعال موفق')
    
    def test_product_deleted_flag(self):
        """آزمایش پرچم حذف محصول"""
        self.product.is_delete = True
        self.product.save()
        self.assertTrue(self.product.is_delete)
        logger.info('✓ آزمایش پرچم حذف محصول موفق')


class ProductQueryTestCase(TestCase):
    """تست‌های جستجوی محصول"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.category = ProductCategory.objects.create(
            title='مواد شیمیایی',
            url_title='mavaad-shimi',
            is_active=True,
            is_delete=False
        )
        self.brand = ProductBrand.objects.create(
            title='برند A',
            url_title='brand-a',
            is_active=True
        )
        
        # ایجاد چندین محصول
        for i in range(5):
            p = Product.objects.create(
                title=f'محصول {i}',
                slug=f'product-{i}',
                price=10000 + (i * 5000),
                inventory=50 + i,
                weight_value=100 + i,
                weight_unit='g',
                brand=self.brand,
                is_active=True,
                is_delete=False
            )
            p.category.add(self.category)
        logger.info('ایجاد 5 محصول تست')
    
    def test_get_all_products(self):
        """آزمایش دریافت تمام محصولات"""
        products = Product.objects.all()
        self.assertEqual(products.count(), 5)
        logger.info('✓ آزمایش دریافت تمام محصولات موفق')
    
    def test_filter_active_products(self):
        """آزمایش فیلتر محصولات فعال"""
        active_products = Product.objects.filter(is_active=True)
        self.assertEqual(active_products.count(), 5)
        logger.info('✓ آزمایش فیلتر محصولات فعال موفق')
    
    def test_filter_by_price(self):
        """آزمایش فیلتر براساس قیمت"""
        expensive_products = Product.objects.filter(price__gte=20000)
        self.assertGreater(expensive_products.count(), 0)
        logger.info('✓ آزمایش فیلتر براساس قیمت موفق')
    
    def test_filter_by_category(self):
        """آزمایش فیلتر براساس دسته‌بندی"""
        products = Product.objects.filter(category=self.category)
        self.assertEqual(products.count(), 5)
        logger.info('✓ آزمایش فیلتر براساس دسته‌بندی موفق')
    
    def test_filter_by_brand(self):
        """آزمایش فیلتر براساس برند"""
        products = Product.objects.filter(brand=self.brand)
        self.assertEqual(products.count(), 5)
        logger.info('✓ آزمایش فیلتر براساس برند موفق')
    
    def test_product_ordering(self):
        """آزمایش مرتب‌سازی محصولات"""
        products = Product.objects.order_by('-price')
        prices = [p.price for p in products]
        self.assertEqual(prices, sorted(prices, reverse=True))
        logger.info('✓ آزمایش مرتب‌سازی محصولات موفق')
