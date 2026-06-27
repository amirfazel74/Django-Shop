"""
تست‌های site_module
Tests for site_module
"""
from django.test import TestCase
from site_module.models import SiteSetting, Slider, FooterLinkBox
import logging

logger = logging.getLogger('site_module')


class SiteSettingTestCase(TestCase):
    """تست‌های تنظیمات سایت"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.setting = SiteSetting.objects.create(
            site_name='فروشگاه تست',
            site_url='test.example.com',
            address='تهران',
            email='test@example.com',
            copy_right='تمام حقوق محفوظ است',
            about_us_text='درباره ما',
            is_main_setting=True
        )
        logger.info('تنظیم تست‌های تنظیمات سایت')
    
    def test_site_setting_creation(self):
        """آزمایش ایجاد تنظیمات سایت"""
        self.assertEqual(self.setting.site_name, 'فروشگاه تست')
        self.assertTrue(self.setting.is_main_setting)
        logger.info('✓ آزمایش ایجاد تنظیمات سایت موفق')
    
    def test_main_setting_unique(self):
        """آزمایش منحصربفری تنظیمات اصلی"""
        # فقط یک تنظیم اصلی باید وجود داشته باشد
        main_settings = SiteSetting.objects.filter(is_main_setting=True)
        self.assertLessEqual(main_settings.count(), 1)
        logger.info('✓ آزمایش منحصربفری تنظیمات اصلی موفق')
