import datetime
from typing import Union

from SmartDjango import Analyse, E
from django.views import View
from wechatpy import parse_message
from wechatpy.events import BaseEvent
from wechatpy.messages import TextMessage, BaseMessage
from wechatpy.replies import TextReply, ArticlesReply

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
        message = parse_message(r.body)  # type: Union[BaseMessage, BaseEvent]

        if message.type == 'event':
            if message.event.startswith('subscribe'):
                reply = ArticlesReply()
                reply.add_article(dict(
                    title='极客 # 如何上手MasterWhole',
                    description='我不是订阅号，我是工具箱。',
                    image='https://res.6-79.cn/disk/cover/WSp5/1574054229.979414/FullSizeRender.jpg?e=1589448273&token=oX6jJmjudP-3BXHJ3A8lYjEQRlQHBc70734ZyTR4:1kQHVWcGdJ82DAwhB3LSqB3uzDQ=',
                    url='https://d.6-79.cn/res/SgARFB',
                ))
                return reply
            else:
                content = '暂不支持回复非文字消息'
        elif message.type == 'text':
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
