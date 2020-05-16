import datetime

from SmartDjango import E
from django.utils.crypto import get_random_string
from smartify import P

from Base.common import ROOT_NAME
from Base.phone import Phone
from Base.service import Service, Parameter, ServiceDepot
from Service.models import ServiceData


@E.register(id_processor=E.idp_cls_prefix())
class BaseServiceError:
    CD_DIR = E("{0}不是工具箱，无法进入")
    NOT_FOUND = E("没有名为{0}的工具箱")
    PARENT = E("没有更大的工具箱啦")
    PHONE_FORMAT = E("手机号格式错误，只支持中国大陆的11位号码")


def phone_validator(phone):
    if len(phone) != 11:
        raise BaseServiceError.PHONE_FORMAT


@Service.register
class BindPhoneService(Service):
    name = 'bind'
    desc = '绑定手机号'
    long_desc = '用于推送其他功能产生的结果\n' \
                '手机号绑定后暂不支持更改\n' \
                '目前只支持中国大陆的手机号码\n' \
                '设置手机号并发送验证码：bind -p13xxxxxxxxx\n' \
                '验证码反馈完成手机绑定：bind -c123456'

    WAIT = 0
    DONE = 1

    PPhone = Parameter(P(read_name='手机号')
                       .process(int)
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

        if data.status:  # 设置手机号
            return '手机号已绑定，暂不支持更改'

        crt_time = datetime.datetime.now().timestamp()
        last_time = data.last_time or 0

        if cls.PPhone.set(parameters):
            phone = cls.PPhone.get(parameters)
            captcha = get_random_string(length=6, allowed_chars='1234567890')

            send_wait = last_time + 60 - crt_time
            if send_wait > 0:
                return '请在%s后重试' % cls.readable_send_wait(send_wait)

            Phone.validate(phone, captcha)
            storage.update(dict(
                captcha=captcha,
                last_time=crt_time,
                attempt=3,
            ))
            return '验证码已发送，五分钟内有效，请使用bind -c命令验证'
        elif cls.PCaptcha.set(parameters):
            if not data.attempt:
                return '请重新发送验证码'

            data.attempt -= 1
            storage.update(data)
            if last_time + 5 * 60 < crt_time:
                return '验证码有效期五分钟已超出，请重新发送'

            captcha = cls.PCaptcha.get(parameters)

            if captcha != data.captcha:
                return '验证码错误，您还有%s次重试机会' % data.attempt
            else:
                storage.user.set_phone(data.phone)
                storage.update(dict(status=cls.DONE))
                return '手机号绑定成功'
        else:
            return '请使用bind -h查看本工具的使用方法'


@Service.register
class CDService(Service):
    name = 'cd'
    desc = '切换工具箱'

    @classmethod
    def run(cls, directory: Service, storage: ServiceData, parameters: dict, *args):
        paths = args[0] if args else ''
        terminal = LSService.find_path(directory, paths)
        storage.update(dict(service=terminal.name))
        return '已进入%s工具箱' % terminal.name


@Service.register
class LSService(Service):
    name = 'ls'
    desc = '查看工具箱'

    PLong = Parameter(P(read_name='是否显示完整信息').default(), short='l')

    @staticmethod
    def find_path(current: Service, paths: str):
        if paths and paths[0] == '/':
            current = ServiceDepot.get(ROOT_NAME)
        paths = paths.split('/')
        for path in paths:
            if path == '..':
                if not current.parent:
                    raise BaseServiceError.PARENT
                current = current.parent
            elif path != '.' and path != '':
                current = current.get(path)
                if not current:
                    raise BaseServiceError.NOT_FOUND(path)
                if not current.as_dir:
                    raise BaseServiceError.CD_DIR(current.name)
        return current

    @classmethod
    def init(cls):
        cls.validate(cls.PLong)

    @classmethod
    def run(cls, directory: Service, storage: ServiceData, parameters: dict, *args):
        paths = args[0] if args else ''
        terminal = cls.find_path(directory, paths)

        long = cls.PLong.set(parameters)
        messages = ['%s中拥有以下工具：' % terminal.name]
        for child in terminal.get_services():
            name = child.name + ['（工具）', '（工具箱）'][child.as_dir]
            if long:
                messages.append('%s\t%s' % (name, child.desc))
            else:
                messages.append(name)
        return '\n'.join(messages)

