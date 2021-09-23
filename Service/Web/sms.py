import datetime
import random
import re

import requests
from bs4 import BeautifulSoup
from smartify import P

from Base.common import ADMIN_PHONE
from Base.lines import Lines
from Base.phone import Phone
from Service.models import Service, Parameter, ServiceData, ParamDict


@Service.register
class SMSService(Service):
    name = 'sms'
    desc = '共享手机短信'
    long_desc = Lines(
        '浏览某些不重要的网站且需要手机号注册时，本工具可以提供共享手机号。',
        '通过sms -g命令获取当前手机号，通过sms -s命令获取接收到的短信（由于手机号共享，收到的短信可能还有其他用户的，您收到的短信也公开），通过sms -r命令获取新手机号'
    )

    SMS_WEB = 'https://temporary-phone-number.com/China-Phone-Number/'

    async_service_task = True

    PGet = Parameter(P(read_name='获取当前手机号').default(), long='get', short='g')
    PShow = Parameter(P(read_name='显示短信').default(), long='show', short='s')
    PRenew = Parameter(P(read_name='获取新手机号').default(), long='renew', short='r')

    @classmethod
    def init(cls):
        cls.validate(cls.PGet, cls.PShow, cls.PRenew)

    @staticmethod
    def item_processor(item):
        time = item.find('time').text
        msg = item.find(class_='direct-chat-text').text.strip().replace('\x1b', '')
        if msg:
            return ['👉%s' % time, msg, '']

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        data = storage.classify()

        if pd.has(cls.PRenew):
            global_storage = cls.get_global_storage()
            global_data = global_storage.classify()
            if not global_data.phones:
                return '暂无可用的共享手机号'
            phone_num = len(global_data.phones)
            phone_index = random.randint(0, phone_num - 1)
            data.phone = global_data.phones[phone_index]
            storage.update(data)
            return data.phone

        if not data.phone:
            return '请使用sms -r命令获取新手机号'

        if pd.has(cls.PGet):
            return data.phone

        if pd.has(cls.PShow):
            url = '%s86%s' % (cls.SMS_WEB, data.phone)
            try:
                with requests.get(url) as r:
                    html = r.content.decode()
            except Exception:
                return '获取短信失败'

            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find_all(class_='direct-chat-msg')
            items = [cls.item_processor(item) for item in items][:10]
            items = list(filter(lambda x: x, items))
            lines = []
            [lines.extend(item) for item in items]

            return Lines(*lines)

        return cls.need_help()

    @classmethod
    def async_service(cls, storage: ServiceData):
        data = storage.classify()

        last_time = data.last_update_time or 0
        crt_time = datetime.datetime.now().timestamp()
        if last_time + 60 * 30 > crt_time:
            return

        data.last_update_time = crt_time
        data.error_web_times = data.error_web_times or 0
        data.error_re_times = data.error_re_times or 0

        try:
            with requests.get(cls.SMS_WEB) as r:
                html = r.content.decode()
            data.error_web_times = 0
        except Exception:
            data.error_web_times += 1
            if data.error_web_times == 3:
                Phone.announce(ADMIN_PHONE, cls, '无法获取网站信息')
            return

        finder = re.findall('"%s86(\d+)"' % cls.SMS_WEB, html, flags=re.S)
        if not finder:
            data.error_re_times += 1
            if data.error_re_times == 3:
                Phone.announce(ADMIN_PHONE, cls, '无法解析手机信息')
            return

        data.phones = [int(phone) for phone in finder]
        storage.update(data)
