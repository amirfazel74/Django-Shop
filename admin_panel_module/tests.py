"""
تست‌های admin_panel_module
Tests for admin_panel_module
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger('admin_panel_module')


class AdminPanelTestCase(TestCase):
    """تست‌های پنل ادمین"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        logger.info('تنظیم تست‌های پنل ادمین')
    
    def test_admin_panel_requires_staff(self):
        """آزمایش نیاز به سطح staff برای پنل ادمین"""
        regular_user = User.objects.create_user(
            username='regular',
            password='pass123'
        )
        self.client.login(username='regular', password='pass123')
        response = self.client.get('/admin-panel/')
        self.assertNotEqual(response.status_code, 200)
        logger.info('✓ آزمایش نیاز به staff موفق')
    
    def test_admin_access_with_superuser(self):
        """آزمایش دسترسی پنل ادمین با سوپریوزر"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin-panel/')
        # اگر پنل ادمین وجود داشته باشد
        self.assertIn(response.status_code, [200, 301, 302])
        logger.info('✓ آزمایش دسترسی پنل ادمین موفق')
