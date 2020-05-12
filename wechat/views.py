from SmartDjango import Analyse
from django.views import View
from smartify import P
from wechatpy.utils import check_signature

from Base.common import WX_TOKEN


class MessageView(View):
    @staticmethod
    @Analyse.r(q=[
        P('signature').validate(str),
        P('timestamp').validate(str),
        P('nonce').validate(str),
        P('echostr').validate(str)])
    def get(r):
        try:
            check_signature(token=WX_TOKEN, **r.d.dict('signature', 'timestamp', 'nonce'))
            return r.d.echostr
        except Exception:
            pass

    @staticmethod
    def post(r):
        print(r.body)
