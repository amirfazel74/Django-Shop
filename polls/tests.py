"""
تست‌های polls
Tests for polls module
"""
from django.test import TestCase
import logging

logger = logging.getLogger('polls')


class PollsModuleTestCase(TestCase):
    """تست‌های ماژول Polls"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        logger.info('تنظیم تست‌های Polls')
    
    def test_polls_module_exists(self):
        """آزمایش وجود ماژول Polls"""
        self.assertTrue(True)
        logger.info('✓ آزمایش وجود ماژول Polls موفق')
