import datetime
import string

from SmartDjango import E
from django.utils.crypto import get_random_string
from smartify import P

from Base.common import msg_idp
from Base.lines import Lines
from Base.phone import Phone
from Service.models import ServiceData, Service, Parameter, ParamDict


@E.register(id_processor=msg_idp)
class BindPhoneMessage:
    PHONE_FORMAT = E("手机号格式错误")
    SEND_WAIT = E("请在{}后重试")
    MODIFY_NOT_ALLOWED = E("手机号已绑定，暂不支持更改")
    CAPTCHA_SENT = E("验证码已发送，五分钟内有效，请使用bind -c命令验证")
    CAPTCHA_RESENT = E('请重新发送验证码')
    TIME_EXPIRED = E('验证码有效期五分钟已超出，请重新发送')
    CAPTCHA_WRONG = E('验证码错误，您还有{}次重试机会')
    SUCCESS = E('手机号绑定成功')
    
    
def phone_validator(phone):
    if phone[0] == '+':
        digits = phone[1:]
    else:
        if len(phone) != 11:
            raise BindPhoneMessage.PHONE_FORMAT
        digits = phone
    for c in digits:
        if c not in string.digits:
            raise BindPhoneMessage.PHONE_FORMAT
    if len(digits) < 6:
        raise BindPhoneMessage.PHONE_FORMAT


@Service.register
class BindPhoneService(Service):
    name = 'bind'
    desc = '绑定手机号'
    long_desc = Lines(
        '用于推送其他功能产生的结果',
        '手机号绑定后允许更改',
        '设置手机号并发送验证码：bind -p13xxxxxxxxx',
        '非中国大陆手机号发送验证码格式为：bind -p+地区代码+手机号',
        '如香港代码为852，则bind -p+85212345678',
        '验证码反馈完成手机绑定：bind -c123456')

    WAIT = 0
    DONE = 1

    PPhone = Parameter(P(read_name='手机号')
                       .process(str)
                       .validate(phone_validator),
                       long='phone', short='p')
    PCaptcha = Parameter(P(read_name='验证码').default(), long='captcha', short='c')

    @classmethod
    def init(cls):
        cls.validate(cls.PPhone, cls.PCaptcha)

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

        # if data.status:  # 设置手机号
        #     raise BindPhoneError.MODIFY_NOT_ALLOWED

        crt_time = datetime.datetime.now().timestamp()
        last_time = data.last_time or 0

        if pd.has(cls.PPhone):
            phone = pd.get(cls.PPhone)
            captcha = get_random_string(length=6, allowed_chars='1234567890')

            send_wait = last_time + 60 - crt_time
            if send_wait > 0:
                raise BindPhoneMessage.SEND_WAIT(send_wait)

            Phone.validate(phone, captcha)
            storage.update(dict(
                phone=phone,
                captcha=captcha,
                last_time=crt_time,
                attempt=3,
            ))
            raise BindPhoneMessage.CAPTCHA_SENT
        elif pd.has(cls.PCaptcha):
            if not data.attempt:
                raise BindPhoneMessage.CAPTCHA_RESENT

            data.attempt -= 1
            storage.update(data)
            if last_time + 5 * 60 < crt_time:
                raise BindPhoneMessage.TIME_EXPIRED

            captcha = pd.get(cls.PCaptcha)
            if captcha != data.captcha:
                raise BindPhoneMessage.CAPTCHA_WRONG(data.attempt)
            return captcha
            storage.user.set_phone(data.phone)
            storage.update(dict(status=cls.DONE))
            raise BindPhoneMessage.SUCCESS
        else:
            return cls.need_help()
