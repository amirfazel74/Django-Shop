from django.dispatch import Signal

# این سیگنال هر بار که پیامک جدیدی در دیتابیس ذخیره شود، شلیک می‌شود
inbound_sms_received = Signal()