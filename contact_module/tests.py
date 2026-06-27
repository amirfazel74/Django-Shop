"""
تست‌های contact_module
Tests for contact_module
"""
from django.test import TestCase, Client
from django.urls import reverse
import logging

logger = logging.getLogger('contact_module')


class ContactViewTestCase(TestCase):
    """تست‌های نمای تماس با ما"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        logger.info('تنظیم تست‌های تماس با ما')
    
    def test_contact_page_status_code(self):
        """آزمایش کد وضعیت صفحه تماس"""
        response = self.client.get('/contact-us/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش کد وضعیت صفحه تماس موفق')
    
    def test_contact_page_contains_form(self):
        """آزمایش وجود فرم در صفحه تماس"""
        response = self.client.get('/contact-us/')
        self.assertIn(b'form' or b'contact', response.content.lower())
        logger.info('✓ آزمایش وجود فرم در صفحه تماس موفق')
