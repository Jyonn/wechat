import datetime
import random

from smartify import P

from Base.lines import Lines
from Module.sms import TemporaryPhoneNumber, SMSMessage, FreeReceiveSMS
from Service.models import Service, Parameter, ServiceData, ParamDict


@Service.register
class SMSService(Service):
    name = 'sms'
    desc = '共享手机短信'
    long_desc = Lines(
        '浏览某些不重要的网站且需要手机号注册时，本工具可以提供共享手机号。',
        '通过sms -g命令获取当前手机号，通过sms -s命令获取接收到的短信（由于手机号共享，收到的短信可能还有其他用户的，您收到的短信也公开），通过sms -r命令获取新手机号'
    )

    async_service_task = True

    PGet = Parameter(P(read_name='获取当前手机号').default(), long='get', short='g')
    PShow = Parameter(P(read_name='显示短信').default(), long='show', short='s')
    PRenew = Parameter(P(read_name='获取新手机号').default(), long='renew', short='r')

    crawler = FreeReceiveSMS()

    @classmethod
    def init(cls):
        cls.validate(cls.PGet, cls.PShow, cls.PRenew)

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        data = storage.classify()

        if pd.has(cls.PRenew):
            global_storage = cls.get_global_storage()
            global_data = global_storage.classify()
            if not global_data.phones:
                raise SMSMessage.NONE
            phone_num = len(global_data.phones)
            phone_index = random.randint(0, phone_num - 1)
            data.phone = global_data.phones[phone_index]
            storage.update(data)
            return data.phone

        if not data.phone:
            raise SMSMessage.NO_PHONE

        if pd.has(cls.PGet):
            return data.phone

        if pd.has(cls.PShow):
            lines = cls.crawler.get_msg(data, service=cls)
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

        data.phones = cls.crawler.get_phone_list(data) or []
        storage.update(data)
