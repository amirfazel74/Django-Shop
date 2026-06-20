# sms_manager/services.py
import datetime

import requests
from django.utils import timezone
import logging
from .models import (
    SMSConfiguration, SMSLine, SMSTemplate,
    ScheduledPack, OutboundSMSLog, InboundSMSLog
)

logger = logging.getLogger(__name__)


class SMSManagerService:
    BASE_URL = "https://api.sms.ir/v1"

    def __init__(self):
        # دریافت تنظیمات و کلید API
        self.config = SMSConfiguration.objects.first()
        if not self.config or not self.config.is_active:
            raise Exception("سیستم پیامکی غیرفعال است یا تنظیمات آن در پنل ادمین ثبت نشده است.")

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": self.config.api_key
        }

    def send_verify(self, mobile: str, template_name: str, parameters: dict) -> bool:
        """
        ارسال پیامک خدماتی/سریع (مثل OTP یا فاکتور)
        """
        try:
            template = SMSTemplate.objects.get(internal_name=template_name, is_active=True)
        except SMSTemplate.DoesNotExist:
            logger.error(f"Template {template_name} not found or inactive.")
            return False

        # تبدیل دیکشنری پایتون به فرمت درخواستی sms.ir
        formatted_params = [{"name": str(k), "value": str(v)} for k, v in parameters.items()]

        payload = {
            "mobile": str(mobile),
            "templateId": template.template_id,
            "parameters": formatted_params
        }

        response = requests.post(f"{self.BASE_URL}/send/verify", headers=self.headers, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", {})
            # ثبت لاگ در دیتابیس
            OutboundSMSLog.objects.create(
                message_id=data.get("messageId"),
                template=template,
                mobile=mobile,
                message_text=f"Template: {template_name} | Params: {parameters}",
                cost=data.get("cost"),
                send_type=OutboundSMSLog.SendTypeChoices.VERIFY
            )
            return True
        else:
            logger.error(f"SMS Verify Error: {response.text}")
            return False

    def fetch_latest_inbound_messages(self, count=100) -> int:
        """
        دریافت تازه‌ترین پیامک‌های دریافتی از سامانه و ذخیره آن‌ها در دیتابیس
        خروجی: تعداد پیامک‌های جدیدی که دریافت و ذخیره شدند
        """
        payload = {"count": count}
        response = requests.get(f"{self.BASE_URL}/receive/latest", headers=self.headers, params=payload, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", [])
            saved_count = 0

            for msg in data:
                receive_id = msg.get("receiveReturnId")

                # برای اطمینان از اینکه پیامک تکراری ذخیره نشود
                if not InboundSMSLog.objects.filter(receive_id=receive_id).exists():
                    # پیدا کردن خطی که پیامک را دریافت کرده
                    number = str(msg.get("number"))
                    line = SMSLine.objects.filter(number=number).first()

                    # تبدیل Unix Time به فرمت تاریخ جنگو
                    received_datetime = timezone.datetime.fromtimestamp(
                        msg.get("receivedDateTime"), tz=datetime.timezone.utc
                    )

                    # ذخیره در جدول لاگ‌های دریافتی
                    inbound_log = InboundSMSLog.objects.create(
                        receive_id=receive_id,
                        line=line,
                        sender_mobile=str(msg.get("mobile")),
                        message_text=msg.get("messageText"),
                        received_at=received_datetime
                    )
                    saved_count += 1

                    # 🚀 بخش حرفه‌ای: فراخوانی سیگنال برای اطلاع به بقیه اپلیکیشن‌ها
                    from .signals import inbound_sms_received
                    inbound_sms_received.send(sender=self.__class__, instance=inbound_log)

            return saved_count
        else:
            logger.error(f"Inbound SMS Fetch Error: {response.text}")
            return 0
    def send_bulk(self, mobiles: list, message_text: str, send_datetime=None, line_number=None) -> bool:
        """
        ارسال پیامک گروهی (تبلیغاتی یا اطلاع‌رسانی جمعی)
        """
        # پیدا کردن خط ارسالی
        if line_number:
            line = SMSLine.objects.filter(number=line_number, is_active=True).first()
        else:
            line = SMSLine.objects.filter(is_default_for_bulk=True, is_active=True).first()

        if not line:
            logger.error("هیچ خط فعال یا پیش‌فرضی برای ارسال گروهی یافت نشد.")
            return False

        payload = {
            "lineNumber": int(line.number),
            "messageText": message_text,
            "mobiles": [str(m) for m in mobiles],
        }

        if send_datetime:
            # تبدیل datetime پایتون به Unix Time (ثانیه)
            payload["SendDateTime"] = int(send_datetime.timestamp())

        response = requests.post(f"{self.BASE_URL}/send/bulk", headers=self.headers, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", {})
            pack_id = data.get("packId")

            # ثبت بسته گروهی در دیتابیس
            pack = ScheduledPack.objects.create(
                pack_id=pack_id,
                line=line,
                total_recipients=len(mobiles),
                total_cost=data.get("cost"),
                scheduled_datetime=send_datetime,
                status=ScheduledPack.StatusChoices.PENDING if send_datetime else ScheduledPack.StatusChoices.SENT
            )

            # ثبت لاگ برای تک‌تک شماره‌ها
            message_ids = data.get("messageIds", [])
            logs = []
            for idx, mobile in enumerate(mobiles):
                msg_id = message_ids[idx] if idx < len(message_ids) else None
                logs.append(OutboundSMSLog(
                    message_id=msg_id,
                    pack=pack,
                    line=line,
                    mobile=mobile,
                    message_text=message_text,
                    send_type=OutboundSMSLog.SendTypeChoices.BULK
                ))
            OutboundSMSLog.objects.bulk_create(logs)
            return True
        else:
            logger.error(f"SMS Bulk Error: {response.text}")
            return False

    def cancel_pack(self, pack_id: str) -> bool:
        """لغو ارسال زمان‌بندی شده"""
        response = requests.delete(f"{self.BASE_URL}/send/scheduled/{pack_id}", headers=self.headers, timeout=10)

        if response.status_code == 200:
            ScheduledPack.objects.filter(pack_id=pack_id).update(status=ScheduledPack.StatusChoices.CANCELED)
            return True
        return False


    def get_credit(self) -> float:
        """دریافت اعتبار پنل"""
        response = requests.get(f"{self.BASE_URL}/credit", headers=self.headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", 0.0)
        return 0.0