import datetime
import re
from typing import List
from urllib.parse import urlparse

import requests
from SmartDjango import E
from smartify import P

from Base.common import md5
from Base.phone import Phone
from Service.models import ServiceData, Parameter, Service


@E.register(id_processor=E.idp_cls_prefix())
class WatchError:
    URL = E("url不规范")
    GET_URL = E("获取网页失败，请重试")


regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def url_validate(url):
    return re.match(regex, url) is not None


@Service.register
class WatchService(Service):
    name = 'watch'
    desc = '网页变化监控'
    long_desc = '当网页发送变化时，将会发送短信提醒，且任务自动结束\n' \
                '⚠️监控时间间隔为5分钟\n' \
                '⚠️暂不支持中文域名网址监控\n' \
                '⚠️网页格式规范，应以http/https开头\n' \
                '👉watch -n百度 https://abc.com'

    async_task = True

    PName = Parameter(P(read_name='监控名').default(), long='name', short='n')
    PCancel = Parameter(P(read_name='取消当前任务').default(), long='cancel')
    PStatus = Parameter(P(read_name='查看当前任务').default(), long='status')

    @staticmethod
    def readable_time(create_time):
        return datetime.datetime.fromtimestamp(create_time).strftime('%m-%d %H:%M')

    @classmethod
    def init(cls):
        cls.validate(cls.PName, cls.PCancel, cls.PStatus)

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        storage.user.require_phone()

        data = storage.classify()
        if cls.PCancel.set(parameters):
            storage.update(dict(
                work=False,
            ))
            return '任务已清空'

        if cls.PStatus.set(parameters):
            if not data.work:
                return '暂无监控任务'
            return '正在监控：%s\n' \
                   '任务开始时间：%s\n' \
                   '已监控次数：%s\n' \
                   % (data.name,
                      cls.readable_time(data.create_time),
                      data.visit_times)

        if not args:
            return cls.need_help()
        url = args[0]
        if not url_validate(url):
            raise WatchError.URL

        key = cls.get_key_of(url)
        name = urlparse(url).netloc
        if cls.PName.set(parameters):
            name = cls.PName.get(parameters)

        crt_time = datetime.datetime.now().timestamp()
        storage.update(dict(
            work=True,
            name=name,
            url=url,
            visit_times=0,
            error_times=0,
            create_time=crt_time,
            last_visit_time=crt_time,
            key=key,
        ))

        return '监控已开启'

    @classmethod
    def async_work_handler(cls, service_data_list: List[ServiceData]):
        for service_data in service_data_list:
            cls.async_work(service_data)

    @staticmethod
    def get_key_of(url):
        try:
            with requests.get(url, timeout=3) as r:
                content = r.content  # type: bytes
        except Exception:
            raise WatchError.GET_URL

        return md5(content)

    @classmethod
    def async_work(cls, service_data: ServiceData):
        data = service_data.classify()
        if not data.work:
            return

        crt_time = datetime.datetime.now().timestamp()
        if data.last_visit_time + 300 > crt_time:
            return

        data.last_visit_time = crt_time
        data.visit_times += 1

        try:
            key = cls.get_key_of(data.url)
            data.error_times = 0
        except E:
            data.error_times += 1
            if data.error_times == 3:
                Phone.announce(service_data.user, cls, '监控任务%s网页连续三次无法访问，已停止任务' % data.name)
                service_data.update(dict(work=False))
            return

        if data.key != key:
            Phone.announce(service_data.user, cls, '监控任务%s的网页发生变化' % data.name)
            service_data.update(dict(work=False))
            return

        service_data.update(data)
