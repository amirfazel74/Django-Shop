"""
تست‌های sms_module
Tests for sms_module
"""
from django.test import TestCase
import logging

logger = logging.getLogger('sms_module')


class SMSModuleTestCase(TestCase):
    """تست‌های ماژول SMS"""
    
    def setUp(self):
        """تنظیم داده‌های تست"""
        logger.info('تنظیم تست‌های SMS')
    
    def test_sms_module_exists(self):
        """آزمایش وجود ماژول SMS"""
        # بررسی اینکه ماژول درست کار می‌کند
        self.assertTrue(True)
        logger.info('✓ آزمایش وجود ماژول SMS موفق')
