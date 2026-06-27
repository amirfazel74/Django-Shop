"""
سیستم لاگ‌گذاری مرکزی برای پروژه
Central logging system for the project
"""
import logging
import logging.handlers
import os
from pathlib import Path
from django.conf import settings

BASE_DIR = Path(settings.BASE_DIR)
LOG_DIR = BASE_DIR / 'logs'

# ایجاد دایرکتوری logs اگر وجود ندارد
LOG_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    تنظیم logger برای یک مدول خاص
    Setup logger for a specific module
    
    Args:
        name: نام logger (معمولا نام مدول)
        log_file: نام فایل لاگ (اختیاری)
        level: سطح logging
    
    Returns:
        logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # جلوگیری از duplicate handlers
    if logger.handlers:
        return logger
    
    # Console Handler - برای console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler - برای فایل لاگ
    if log_file is None:
        log_file = f'{name}.log'
    
    log_path = LOG_DIR / log_file
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # RotatingFileHandler - برای backup خودکار لاگ‌ها
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    rotating_handler.setLevel(level)
    rotating_handler.setFormatter(file_formatter)
    
    return logger


# Loggers برای مدول‌های مختلف
account_logger = setup_logger('account_module', 'account.log')
product_logger = setup_logger('product_module', 'product.log')
order_logger = setup_logger('order_module', 'order.log')
payment_logger = setup_logger('payment', 'payment.log')
otp_logger = setup_logger('otp_auth', 'otp.log')
sms_logger = setup_logger('sms_module', 'sms.log')
article_logger = setup_logger('article_module', 'article.log')
contact_logger = setup_logger('contact_module', 'contact.log')
user_panel_logger = setup_logger('user_panel_module', 'user_panel.log')
admin_logger = setup_logger('admin_panel_module', 'admin_panel.log')
home_logger = setup_logger('home_module', 'home.log')

# Main logger
main_logger = setup_logger('eshop', 'eshop.log')
