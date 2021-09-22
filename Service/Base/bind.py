import datetime
import string

from SmartDjango import E
from django.utils.crypto import get_random_string
from smartify import P

from Base.para import Para
from Base.phone import Phone
from Service.models import ServiceData, Service, Parameter


@E.register(id_processor=E.idp_cls_prefix())
class BindPhoneError:
    PHONE_FORMAT = E("手机号格式错误")
    
    
def phone_validator(phone):
    if phone[0] == '+':
        digits = phone[1:]
    else:
        if len(phone) != 11:
            raise BindPhoneError.PHONE_FORMAT
        digits = phone
    for c in digits:
        if c not in string.digits:
            raise BindPhoneError.PHONE_FORMAT


@Service.register
class BindPhoneService(Service):
    name = 'bind'
    desc = '绑定手机号'
    long_desc = Para(
        '用于推送其他功能产生的结果',
        '手机号绑定后允许更改',
        '设置手机号并发送验证码：bind -p13xxxxxxxxx',
        '非中国大陆手机号发送验证码格式为：bind -p+地区代码+手机号',
        '如香港代码为886，则bind -p+88612345678',
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
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        data = storage.classify()

        # if data.status:  # 设置手机号
        #     return '手机号已绑定，暂不支持更改'

        crt_time = datetime.datetime.now().timestamp()
        last_time = data.last_time or 0

        if cls.PPhone.is_set_in(parameters):
            phone = cls.PPhone.get_in(parameters)
            captcha = get_random_string(length=6, allowed_chars='1234567890')

            send_wait = last_time + 60 - crt_time
            if send_wait > 0:
                return '请在%s后重试' % cls.readable_send_wait(send_wait)

            Phone.validate(phone, captcha)
            storage.update(dict(
                phone=phone,
                captcha=captcha,
                last_time=crt_time,
                attempt=3,
            ))
            return '验证码已发送，五分钟内有效，请使用bind -c命令验证'
        elif cls.PCaptcha.is_set_in(parameters):
            if not data.attempt:
                return '请重新发送验证码'

            data.attempt -= 1
            storage.update(data)
            if last_time + 5 * 60 < crt_time:
                return '验证码有效期五分钟已超出，请重新发送'

            captcha = cls.PCaptcha.get_in(parameters)

            if captcha != data.captcha:
                return '验证码错误，您还有%s次重试机会' % data.attempt
            else:
                storage.user.set_phone(data.phone)
                storage.update(dict(status=cls.DONE))
                return '手机号绑定成功'
        else:
            return cls.need_help()
