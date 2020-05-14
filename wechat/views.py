import datetime

from SmartDjango import Analyse, E
from django.views import View
from wechatpy import parse_message
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply

from Base.auth import Auth
from Base.common import wechat_client
from Base.message_handler import MessageHandler
from Config.models import Config, CI
from User.models import UserP, User


class MessageView(View):
    @staticmethod
    @Analyse.r(q=['signature', 'timestamp', 'nonce', 'echostr'])
    @Auth.wechat
    def get(r):
        return r.d.echostr

    @staticmethod
    @Analyse.r(q=['signature', 'timestamp', 'nonce', UserP.openid])
    @Auth.wechat
    def post(r):
        user = r.d.user
        print(r.body)
        message = parse_message(r.body)

        if message.type == 'text':
            try:
                content = MessageHandler(user, message.content).message
            except E as e:
                content = e.message
        else:
            content = '暂不支持回复非文字消息'

        return TextReply(
            message=message,
            content=content).render()


class TestView(View):
    @staticmethod
    @Analyse.r(b=['command'])
    def post(r):
        user = User.objects.get(pk=1)
        try:
            return MessageHandler(user, r.d.command).message
        except E as e:
            return e.message


class AccessTokenView(View):
    @staticmethod
    def get(r):
        expire_time = float(Config.get_value_by_key(CI.WX_ACCESS_TOKEN_EXPIRE) or '0')
        crt_time = datetime.datetime.now().timestamp()
        if crt_time + 10 * 60 > expire_time:
            data = wechat_client.fetch_access_token()
            Config.update_value(CI.WX_ACCESS_TOKEN, data['access_token'])
            Config.update_value(CI.WX_ACCESS_TOKEN_EXPIRE, str(crt_time + data['expires_in']))
        return 0
