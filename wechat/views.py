import datetime

from SmartDjango import Analyse
from django.views import View
from smartify import P
from wechatpy.utils import check_signature

from Base.common import WX_TOKEN, wechat_client
from Config.models import Config, CI


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


class AccessTokenView(View):
    @staticmethod
    def get(r):
        expire_time = float(Config.get_value_by_key(CI.WX_ACCESS_TOKEN_EXPIRE) or '0')
        crt_time = datetime.datetime.now().timestamp()
        if crt_time + 10 * 60 > expire_time:
            data = wechat_client.fetch_access_token()
            Config.update_value(CI.WX_ACCESS_TOKEN, data['access_token'])
            Config.update_value(CI.WX_ACCESS_TOKEN_EXPIRE, str(crt_time + data['expires_in']))
