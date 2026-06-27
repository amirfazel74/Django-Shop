"""
تست‌های user_panel_module
Tests for user_panel_module
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from order_module.models import Order
import logging

User = get_user_model()
logger = logging.getLogger('user_panel_module')


class UserPanelViewTestCase(TestCase):
    """تست‌های نمای پنل کاربر"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='paneluser',
            email='panel@example.com',
            password='pass123'
        )
        logger.info('تنظیم تست‌های پنل کاربر')
    
    def test_user_panel_requires_login(self):
        """آزمایش الزام ورود برای پنل کاربر"""
        response = self.client.get('/user/')
        self.assertNotEqual(response.status_code, 200)
        logger.info('✓ آزمایش الزام ورود موفق')
    
    def test_user_panel_with_login(self):
        """آزمایش دسترسی پنل با ورود"""
        self.client.login(username='paneluser', password='pass123')
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش دسترسی پنل با ورود موفق')
