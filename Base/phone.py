from urllib.parse import urlencode

import requests
from SmartDjango import E

from Base.common import YP_KEY
from Service.models import ServiceData
from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class PhoneError:
    SEND = E("短信发送失败")


class Phone:
    templates = dict(
        validate='【MasterWhole】您的验证码是#code#',
        announce='【MasterWhole】命令#name#的运行结果已出：#message#',
    )

    send_api = "https://sms.yunpian.com/v2/sms/single_send.json"

    @classmethod
    def _send(cls, phone, text):
        try:
            params = urlencode(dict(
                apikey=YP_KEY,
                text=text,
                mobile=phone))

            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }

            requests.post(cls.send_api, params, headers=headers).close()
        except Exception:
            raise PhoneError.SEND

    @classmethod
    def validate(cls, phone, code):
        text = cls.templates['validate'].replace('#code#', code)
        cls._send(phone, text)

    @classmethod
    def announce(cls, user, service, message):
        if isinstance(user, ServiceData):
            user = user.user
        if isinstance(user, User):
            user = user.phone

        text = cls.templates['announce'].replace(
            '#name#', '[%s - %s]' % (service.name, service.desc)).replace('#message#', message)
        cls._send(user, text)
