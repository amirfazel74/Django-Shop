"""
Django Shell Script for Running Tests
راهنمای اجرای تست‌های Django
"""

# اجرای تمام تست‌ها:

# python manage.py test

# اجرای تست‌های مدول خاص:

# python manage.py test account_module

# python manage.py test product_module

# python manage.py test order_module

# اجرای تست با verbose:

# python manage.py test --verbosity=2

# اجرای تست‌های خاص:

# python manage.py test account_module.tests.UserModelTestCase

# python manage.py test account_module.tests.UserModelTestCase.test_user_creation

# اجرای تست‌های یکپارچگی:

# python manage.py test tests_integration

# مشاهده coverage (نیاز به coverage نصب شده):

# pip install coverage

# coverage run --source='.' manage.py test

# coverage report

# coverage html

# اجرای تست‌ها بدون Migrations:

# python manage.py test --keepdb

# اجرای تست با parallel:

# pip install django-parallel-tests

# python manage.py test --parallel

# مشاهده لاگ‌های تست:

# logs/ دایرکتوری شامل فایل‌های لاگ است

# - django.log: لاگ‌های کلی Django

# - account.log: لاگ‌های account_module

# - product.log: لاگ‌های product_module

# - order.log: لاگ‌های order_module

# - security.log: لاگ‌های امنیتی
