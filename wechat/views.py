import datetime
from typing import Union

from SmartDjango import Analyse, E
from django.views import View
from wechatpy import parse_message
from wechatpy.events import BaseEvent
from wechatpy.messages import TextMessage, BaseMessage
from wechatpy.replies import TextReply, ArticlesReply

from Base.auth import Auth
from Base.common import wechat_client, SECRET_KEY
from Base.handler import MessageHandler
from Config.models import Config, CI
from Service.models import ServiceDepot, ServiceData
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
        message = parse_message(r.body)  # type: Union[TextMessage, BaseEvent]

        if message.type == 'event':
            if message.event.startswith('subscribe'):
                content = '欢迎关注，<a href="https://mp.weixin.qq.com/s/Md6iCGh3OgIr5l2dOMeunw">立即体验MasterWhole</a>！'
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
    @Auth.only_localhost
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


class ServiceView(View):
    @staticmethod
    @Analyse.r(q=['secret_key'])
    def get(r):
        if SECRET_KEY != r.d.secret_key:
            return 0

        for name in ServiceDepot.services:
            service = ServiceDepot.services[name]
            if service.async_user_task:
                service_data_list = ServiceData.objects.filter(service=name)
                service.async_user_handler(service_data_list)
            if service.async_service_task:
                service.async_service(ServiceData.get_or_create(service, None))

        return '异步任务完成'
