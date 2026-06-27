"""
تست‌های otp_auth
Tests for otp_auth module
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger('otp_auth')


class OTPAuthTestCase(TestCase):
    """تست‌های احراز هویت OTP"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='otpuser',
            email='otp@example.com',
            password='pass123',
            mobile='09123456789'
        )
        logger.info('تنظیم تست‌های OTP')
    
    def test_auth_page_status_code(self):
        """آزمایش کد وضعیت صفحه احراز هویت"""
        response = self.client.get('/auth/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش کد وضعیت صفحه احراز هویت موفق')
    
    def test_login_functionality(self):
        """آزمایش کارکرد ورود"""
        logged_in = self.client.login(username='otpuser', password='pass123')
        self.assertTrue(logged_in)
        logger.info('✓ آزمایش کارکرد ورود موفق')
