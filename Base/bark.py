from urllib.parse import quote

import requests
from smartdjango import Error, Code

from Service.models import ServiceData
from User.models import User


@Error.register
class BarkErrors:
    SEND = Error("Bark发送失败", code=Code.InternalServerError)


class Bark:
    templates = dict(
        validate='您的验证码是#code#',
        announce='命令#name#的运行结果已出：#message#',
    )

    @classmethod
    def _send(cls, bark, text):
        if not bark.endswith('/'):
            bark += '/'
        path = '%s%s/%s' % (bark, quote('MasterWhole', safe=''), quote(text, safe=''))
        try:
            requests.get(path).close()
        except Exception as e:
            raise BarkErrors.SEND(details=e)

    @classmethod
    def validate(cls, bark, code):
        text = cls.templates['validate'].replace('#code#', code)
        cls._send(bark, text)

    @classmethod
    def announce(cls, user, service, message):
        if isinstance(user, ServiceData):
            user = user.user
        if isinstance(user, User):
            user = user.bark

        text = cls.templates['announce'].replace(
            '#name#', '%s（%s）' % (service.name, service.desc)).replace('#message#', message)
        cls._send(user, text)
