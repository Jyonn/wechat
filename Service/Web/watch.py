import datetime
import re
from typing import List
from urllib.parse import urlparse

import requests
from smartdjango import Error, Code, Validator

from Base.bark import Bark
from Base.common import md5
from Base.lines import Lines
from Service.models import ServiceData, Parameter, Service, ParamDict


@Error.register
class WatchErrors:
    URL = Error("URL不规范", code=Code.BadRequest)
    GET_URL = Error("获取网页失败，请重试", code=Code.BadRequest)


regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
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
    long_desc = Lines(
        '当网页发送变化时，将会发送短信提醒，且任务自动结束',
        '⚠️监控最短时间单位为1分钟',
        '⚠️暂不支持中文域名网址监控',
        '⚠️网页格式规范，应以http/https开头',
        '👉watch -n百度 https://www.baidu.com',
        '👉watch -i2 https://www.zju.edu.cn')

    async_user_task = True

    PInterval = Parameter(Validator(verbose_name='监控时间单位').to(int), long='interval', short='i', default=5)
    PName = Parameter(Validator(verbose_name='监控名').default(None).null(), long='name', short='n')
    PCancel = Parameter(Validator(verbose_name='取消当前任务').default(None).null(), long='cancel')
    PStatus = Parameter(Validator(verbose_name='查看当前任务').default(None).null(), long='status')

    @staticmethod
    def readable_time(create_time):
        return datetime.datetime.fromtimestamp(create_time).strftime('%m-%d %H:%M')

    @classmethod
    def init(cls):
        cls.validate(cls.PName, cls.PCancel, cls.PStatus, cls.PInterval)

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        storage.user.require_bark()

        data = storage.classify()
        if pd.has(cls.PCancel):
            data.work = False
            storage.update(data)
            return '任务已取消'

        if pd.has(cls.PStatus):
            if not data.work:
                return '暂无监控任务'
            return Lines(
                '正在监控：%s' % data.name,
                '任务开始时间：%s' % cls.readable_time(data.create_time),
                '已监控次数：%s' % data.visit_times,
                '监控时间间隔：%s分钟' % (data.interval or cls.PInterval.p.default_value)
            )

        if not args:
            return cls.need_help()
        url = args[0]
        if not url_validate(url):
            raise WatchErrors.URL

        key = cls.get_key_of(url)
        name = urlparse(url).netloc
        if pd.has(cls.PName):
            name = pd.get(cls.PName)
        interval = pd.get(cls.PInterval)

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
            interval=interval,
        ))

        return '监控已开启'

    @classmethod
    def async_user_handler(cls, storage_list: List[ServiceData]):
        for service_data in storage_list:
            cls.async_user(service_data)

    @staticmethod
    def get_key_of(url):
        try:
            with requests.get(url, timeout=3) as r:
                content = r.content  # type: bytes
        except Exception:
            raise WatchErrors.GET_URL

        return md5(content)

    @classmethod
    def async_user(cls, storage: ServiceData):
        data = storage.classify()
        data.interval = data.interval or cls.PInterval.p.default_value

        if not data.work:
            return

        crt_time = datetime.datetime.now().timestamp()
        if data.last_visit_time + 60 * data.interval > crt_time:
            return

        data.last_visit_time = crt_time
        data.visit_times += 1

        try:
            key = cls.get_key_of(data.url)
            data.error_times = 0
        except Error:
            data.error_times += 1
            if data.error_times == 3:
                Bark.announce(storage.user, cls, '监控任务%s网页连续三次无法访问，已停止任务' % data.name)
                storage.update(dict(work=False))
            return

        if data.key != key:
            Bark.announce(storage.user, cls, '监控任务%s的网页发生变化' % data.name)
            storage.update(dict(work=False))
            return

        storage.update(data)
