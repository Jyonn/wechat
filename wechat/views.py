import datetime
from typing import Union

from SmartDjango import Analyse, E
from django.views import View
from wechatpy import parse_message
from wechatpy.events import BaseEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply

from Base.auth import Auth
from Base.common import wechat_client, SECRET_KEY, body_packer, qiX_client
from Base.handler import MessageHandler
from Base.idx import tidx
from Config.models import Config, CI
from Service.models import ServiceDepot, ServiceData
from User.models import UserP, User


class MessageView(View):
    @staticmethod
    @body_packer
    @Analyse.r(q=['signature', 'timestamp', 'nonce', 'echostr'])
    @Auth.wechat
    def get(r):
        return r.d.echostr

    @staticmethod
    @body_packer
    @Analyse.r(q=['signature', 'timestamp', 'nonce', UserP.openid])
    @Auth.wechat
    def post(r):
        user = r.d.user
        message = parse_message(r.body)  # type: Union[TextMessage, BaseEvent]

        if message.type == 'event':
            if message.event.startswith('subscribe'):
                content = '欢迎关注，<a href="https://mp.weixin.qq.com/s/Md6iCGh3OgIr5l2dOMeunw">' \
                          '立即体验MasterWhole</a>！'
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
    @body_packer
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
    def get(_):
        crt_time = datetime.datetime.now().timestamp()

        if tidx.allow_key_maps_constructor():
            # python >= 3.6
            client = tidx(client='fetch_access_token', expire=0, access_token=0)
        else:
            client = tidx('client', 'expire', 'access_token').map(fetch_access_token=0)

        clients = [
            client(wechat_client, CI.WX_ACCESS_TOKEN_EXPIRE, CI.WX_ACCESS_TOKEN),
            client(qiX_client, CI.QIX_ACCESS_TOKEN_EXPIRE, CI.QIX_ACCESS_TOKEN),
        ]

        for client in clients:
            expire_time = float(Config.get_value_by_key(client.expire) or '0')
            if crt_time + 10 * 60 > expire_time:
                data = client.fetch_access_token()
                Config.update_value(client.access_token, data['access_token'])
                Config.update_value(client.expire, str(crt_time + data['expires_in']))

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
