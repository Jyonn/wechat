import datetime

from SmartDjango import E
from django.utils.crypto import get_random_string
from smartify import P

from Base.common import msg_idp
from Base.lines import Lines
from Base.bark import Bark
from Service.models import ServiceData, Service, Parameter, ParamDict


@E.register(id_processor=msg_idp)
class BindBarkMessage:
    SEND_WAIT = E("请在{}后重试")
    MODIFY_NOT_ALLOWED = E("Bark已绑定，暂不支持更改")
    CAPTCHA_SENT = E("验证码已发送，五分钟内有效，请使用bark -c命令验证")
    CAPTCHA_RESENT = E('请重新发送验证码')
    TIME_EXPIRED = E('验证码有效期五分钟已超出，请重新发送')
    CAPTCHA_WRONG = E('验证码错误，您还有{}次重试机会')
    SUCCESS = E('Bark绑定成功')
    
    
@Service.register
class BindBarkService(Service):
    name = 'bark'
    desc = '绑定Bark'
    long_desc = Lines(
        '用于推送其他功能产生的结果',
        'Bark（仅支持iOS设备）绑定后允许更改',
        '下载地址：https://bark.day.app/#/',
        '设置Bark并发送验证码：bark -uhttps://api.day.app/xxxxx',
        '验证码反馈完成手机绑定：bark -c123456')

    WAIT = 0
    DONE = 1

    PBark = Parameter(P(read_name='Bark地址').process(str), long='uri', short='u')
    PCaptcha = Parameter(P(read_name='验证码').default(), long='captcha', short='c')

    @classmethod
    def init(cls):
        cls.validate(cls.PBark, cls.PCaptcha)

    @staticmethod
    def readable_send_wait(send_wait: int):
        s = ''
        send_wait = int(send_wait)
        if send_wait // 60:
            s += '%s分' % (send_wait // 60)
        if send_wait % 60:
            s += '%s秒' % (send_wait % 60)
        return s

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        data = storage.classify()

        crt_time = datetime.datetime.now().timestamp()
        last_time = data.last_time or 0

        if pd.has(cls.PBark):
            bark = pd.get(cls.PBark)
            captcha = get_random_string(length=6, allowed_chars='1234567890')

            send_wait = last_time + 60 - crt_time
            if send_wait > 0:
                raise BindBarkMessage.SEND_WAIT(send_wait)

            Bark.validate(bark, captcha)
            storage.update(dict(
                bark=bark,
                captcha=captcha,
                last_time=crt_time,
                attempt=3,
            ))
            raise BindBarkMessage.CAPTCHA_SENT
        elif pd.has(cls.PCaptcha):
            if not data.attempt:
                raise BindBarkMessage.CAPTCHA_RESENT

            data.attempt -= 1
            storage.update(data)
            if last_time + 5 * 60 < crt_time:
                raise BindBarkMessage.TIME_EXPIRED

            captcha = pd.get(cls.PCaptcha)
            if captcha != data.captcha:
                raise BindBarkMessage.CAPTCHA_WRONG(data.attempt)

            storage.user.set_bark(data.bark)
            storage.update(dict(status=cls.DONE))
            raise BindBarkMessage.SUCCESS
        else:
            return cls.need_help()
