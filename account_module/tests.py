"""
تست‌های account_module
Tests for account_module
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import logging

User = get_user_model()
logger = logging.getLogger('account_module')


class UserModelTestCase(TestCase):
    """تست‌های مدل User"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='تست',
            last_name='کاربر',
            mobile='09123456789'
        )
        logger.info(f'ایجاد کاربر تست: {self.user.username}')
    
    def test_user_creation(self):
        """آزمایش ایجاد کاربر"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.mobile, '09123456789')
        logger.info('✓ آزمایش ایجاد کاربر موفق')
    
    def test_user_str_representation(self):
        """آزمایش نمایش متنی کاربر"""
        expected = f'{self.user.first_name} {self.user.last_name}'
        self.assertEqual(str(self.user), expected)
        logger.info('✓ آزمایش نمایش متنی موفق')
    
    def test_user_without_name(self):
        """آزمایش نمایش کاربر بدون نام"""
        user = User.objects.create_user(
            username='noname',
            password='pass123'
        )
        self.assertEqual(str(user), 'noname')
        logger.info('✓ آزمایش نمایش کاربر بدون نام موفق')
    
    def test_user_password_hashing(self):
        """آزمایش هش شدن رمزعبور"""
        self.assertNotEqual(self.user.password, 'testpass123')
        self.assertTrue(self.user.check_password('testpass123'))
        logger.info('✓ آزمایش هش شدن رمزعبور موفق')
    
    def test_unique_mobile(self):
        """آزمایش منحصربفری شماره موبایل"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='duplicate',
                mobile='09123456789',
                password='pass123'
            )
        logger.info('✓ آزمایش منحصربفری شماره موبایل موفق')
    
    def test_user_email_active_code(self):
        """آزمایش کد فعالسازی ایمیل"""
        self.assertIsNotNone(self.user.email_active_code)
        self.assertIsInstance(self.user.email_active_code, str)
        logger.info('✓ آزمایش کد فعالسازی ایمیل موفق')
    
    def test_user_avatar_field(self):
        """آزمایش فیلد آواتار"""
        # ImageField خالی است اما string خالی بر می‌گرداند
        self.assertTrue(str(self.user.avatar) in ['None', ''])
        logger.info('✓ آزمایش فیلد آواتار موفق')
    
    def test_user_about_field(self):
        """آزمایش فیلد درباره کاربر"""
        self.user.about_user = 'من یک کاربر تست هستم'
        self.user.save()
        self.assertEqual(self.user.about_user, 'من یک کاربر تست هستم')
        logger.info('✓ آزمایش فیلد درباره کاربر موفق')
    
    def test_user_address_field(self):
        """آزمایش فیلد آدرس"""
        self.user.address = 'تهران، خیابان انقلاب'
        self.user.save()
        self.assertEqual(self.user.address, 'تهران، خیابان انقلاب')
        logger.info('✓ آزمایش فیلد آدرس موفق')


class UserAuthenticationTestCase(TestCase):
    """تست‌های احراز هویت کاربر"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpass123'
        )
        logger.info('تنظیم تست احراز هویت')
    
    def test_user_authentication(self):
        """آزمایش احراز هویت کاربر"""
        self.assertTrue(self.user.is_authenticated)
        logger.info('✓ آزمایش احراز هویت موفق')
    
    def test_inactive_user(self):
        """آزمایش کاربر غیرفعال"""
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.user.is_active)
        logger.info('✓ آزمایش کاربر غیرفعال موفق')
    
    def test_staff_user(self):
        """آزمایش کاربر کارمند"""
        self.user.is_staff = True
        self.user.save()
        self.assertTrue(self.user.is_staff)
        logger.info('✓ آزمایش کاربر کارمند موفق')
    
    def test_superuser_creation(self):
        """آزمایش ایجاد سوپریوزر"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        logger.info('✓ آزمایش ایجاد سوپریوزر موفق')


class UserQueryTestCase(TestCase):
    """تست‌های جستجوی کاربر"""
    
    def setUp(self):
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        logger.info('ایجاد کاربران تست')
    
    def test_get_user_by_username(self):
        """آزمایش جستجوی کاربر براساس نام کاربری"""
        user = User.objects.get(username='user1')
        self.assertEqual(user.email, 'user1@example.com')
        logger.info('✓ آزمایش جستجوی کاربر براساس نام کاربری موفق')
    
    def test_get_user_by_email(self):
        """آزمایش جستجوی کاربر براساس ایمیل"""
        user = User.objects.get(email='user2@example.com')
        self.assertEqual(user.username, 'user2')
        logger.info('✓ آزمایش جستجوی کاربر براساس ایمیل موفق')
    
    def test_user_count(self):
        """آزمایش تعداد کاربران"""
        count = User.objects.count()
        self.assertEqual(count, 2)
        logger.info('✓ آزمایش تعداد کاربران موفق')
    
    def test_filter_active_users(self):
        """آزمایش فیلتر کاربران فعال"""
        active_users = User.objects.filter(is_active=True)
        self.assertEqual(active_users.count(), 2)
        logger.info('✓ آزمایش فیلتر کاربران فعال موفق')
