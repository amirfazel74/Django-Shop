"""
تست‌های article_module
Tests for article_module
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from datetime import datetime
import logging

User = get_user_model()
logger = logging.getLogger('article_module')


class ArticleViewTestCase(TestCase):
    """تست‌های نمای مقالات"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        self.client = Client()
        logger.info('تنظیم تست‌های مقالات')
    
    def test_articles_page_status_code(self):
        """آزمایش کد وضعیت صفحه مقالات"""
        response = self.client.get('/articles/')
        self.assertEqual(response.status_code, 200)
        logger.info('✓ آزمایش کد وضعیت صفحه مقالات موفق')
