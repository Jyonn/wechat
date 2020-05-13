from typing import List, Union

from SmartDjango import E
from smartify import P

from Base.UnicodeFont.unicode_font import LNormalItalic, LTiny
from Service.models import ServiceData


@E.register()
class ServiceError:
    PARAM_NO_VALUE = E("命令需要{0}参数")
    PARAM_NAME = E("参数命名错误")
    DIR_NOT_CALLABLE = E("目录无法运行")


class Parameter:
    class NotSet:
        pass

    class NotFound:
        pass

    def __init__(self,
                 p: Union[P, str, None] = None,
                 long=None,
                 short=None,
                 default=NotSet,
                 allow_default=True):
        self.p = P(p) if isinstance(p, str) else p
        self.short = short
        self.long = long
        self.default = default
        self.allow_default = allow_default

        if not self.short and not self.long:
            raise ServiceError.PARAM_NAME

    def get_from(self, kwargs: dict):
        keys = []
        if self.short:
            keys.append('-' + self.short)
        if self.long:
            keys.append('--' + self.long)

        for key in keys:
            if key in kwargs:
                return kwargs[key]
        return self.NotFound

    def __str__(self):
        if self.short:
            if self.long:
                return '-%s(--%s)' % (self.short, self.long)
            else:
                return '-%s' % self.short
        return '--%s' % self.long

    def set(self, parameters: dict):
        if self in parameters:
            return parameters[self] != self.NotSet
        return False


class Service:
    name = 'NAME'
    desc = 'DESCRIPTION'
    long_desc = """暂无详细说明"""

    as_dir = False
    parent = None

    PHelper = Parameter(P(read_name='获取帮助').default(), long='help', short='h')
    PInline = Parameter(P(read_name='批处理模式').default(), long='inline')

    __parameters = [PHelper, PInline]  # type: List[Parameter]
    __services = []  # type: List['Service']

    @classmethod
    def helper(cls):
        messages = ['%s: %s' % (cls.name, cls.desc), cls.long_desc, '', '功能参数说明：']
        for parameter in cls.__parameters:
            messages.append('%s: %s' % (LTiny.translate(str(parameter)), parameter.p.read_name))
        return '\n'.join(messages)

    @classmethod
    def work(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        if cls.as_dir:
            raise ServiceError.DIR_NOT_CALLABLE

        if parameters[cls.PHelper] == Parameter.NotSet:
            return cls.run(directory, storage, parameters, *args)
        return cls.helper()

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        pass

    @classmethod
    def get(cls, name):
        for service in cls.__services:
            if service.name == name:
                return service

    @classmethod
    def process_parameters(cls, kwargs: dict):
        parameters = dict()
        for parameter in cls.__parameters:
            value = parameter.get_from(kwargs)
            if value == Parameter.NotFound:
                if parameter.default == Parameter.NotSet and not parameter.allow_default:
                    raise ServiceError.PARAM_NO_VALUE(str(parameter))
                else:
                    value = parameter.default
            else:
                _, value = parameter.p.run(value)
            parameters[parameter] = value
        return parameters

    @classmethod
    def register(cls, service: 'Service'):
        ServiceDepot.register(service)
        return service

    @classmethod
    def contains(cls, *services):
        if cls.__services:
            cls.__services.extend(services)
        else:
            cls.__services = list(services)
        for service in services:
            service.parent = cls

    @classmethod
    def validate(cls, *parameters):
        cls.__parameters = cls.__parameters + list(parameters)

    @classmethod
    def get_services(cls):
        return cls.__services

    @classmethod
    def get_console_line(cls):
        paths = ''
        service = cls
        while service.name != 'root':
            paths = '/' + service.name + paths
            service = service.parent
        return '$ %s > ' % (paths or '/')


class ServiceDepot:
    services = dict()

    @classmethod
    def register(cls, service: Service):
        if service.name in cls.services:
            raise ValueError(service.name + '重复')

        cls.services[service.name] = service

    @classmethod
    def get(cls, service_name):
        return cls.services.get(service_name)
