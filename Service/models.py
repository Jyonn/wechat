import json

from SmartDjango import models
from django.db.models import F

from typing import List, Union, Dict

from SmartDjango import E
from oba import Obj
from smartify import P

from Base.common import msg_idp


@E.register(id_processor=msg_idp)
class ServiceMessage:
    PARAM_NO_VALUE = E("命令需要{0}参数")
    PARAM_NAME = E("参数命名错误")
    DIR_NOT_CALLABLE = E("目录无法运行")


class Parameter:
    """参数"""

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
            raise ServiceMessage.PARAM_NAME

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

    def is_set_in(self, pd):
        if self in pd.p_dict:
            return pd.p_dict[self] != self.NotSet
        return False

    def get_in(self, pd):
        return pd.p_dict[self]


class ParamDict:
    def __init__(self, p_dict: dict):
        self.p_dict = p_dict

    def has(self, key: Parameter):
        return key.is_set_in(self)

    def get(self, key: Parameter):
        return key.get_in(self)


class ServiceData(models.Model):
    """服务数据"""
    service = models.CharField(
        max_length=10,
    )

    user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
        null=True,
    )

    data = models.TextField(
        null=True,
        default=None,
    )

    parameters = models.TextField(
        null=True,
        default=None,
    )

    interact_times = models.IntegerField(default=1)

    @classmethod
    def get_or_create(cls, service, user):
        if not isinstance(service, str):
            service = service.name

        try:
            service_data = cls.objects.get(service=service, user=user)
            service_data.interact()
            return service_data
        except cls.DoesNotExist:
            return cls.objects.create(service=service, user=user)

    def interact(self):
        self.interact_times = F('interact_times') + 1
        self.save()
        self.refresh_from_db()

    def jsonify(self):
        data = self.data or '{}'
        return json.loads(data)

    def classify(self):
        return Obj(self.jsonify())

    def update(self, data):
        data = Obj.raw(data)
        self.data = json.dumps(data, ensure_ascii=False)
        self.save()

    def fetch_parameters(self):
        return json.loads(self.parameters or '{}')

    def store_parameters(self, parameters):
        self.parameters = json.dumps(parameters, ensure_ascii=False)
        self.save()


class Service:
    """服务"""
    name = 'NAME'
    desc = 'DESCRIPTION'
    long_desc = """暂无详细说明"""

    as_dir = False
    parent = None
    async_user_task = False
    async_service_task = False

    PHelper = Parameter(P(read_name='获取帮助').default(), long='help', short='h')
    PInline = Parameter(P(read_name='批处理模式').default(), long='inline')

    __parameters = [PHelper, PInline]  # type: List[Parameter]
    __services = []  # type: List['Service']

    @classmethod
    def init(cls):
        pass

    @classmethod
    def get_global_storage(cls):
        return ServiceData.get_or_create(cls.name, None)

    @classmethod
    def need_help(cls):
        return '请使用%s -h查看本工具的使用方法' % cls.name

    @classmethod
    def helper(cls):
        messages = ['%s: %s' % (cls.name, cls.desc), str(cls.long_desc), '', '功能参数说明：']
        for parameter in cls.__parameters:
            messages.append('%s: %s' % (str(parameter), parameter.p.read_name))
        return '\n'.join(messages)

    @classmethod
    def work(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        if cls.as_dir:
            raise ServiceMessage.DIR_NOT_CALLABLE

        if not pd.has(cls.PHelper):
            return str(cls.run(directory, storage, pd, *args))
        return cls.helper()

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        pass

    @classmethod
    def get(cls, name):
        for service in cls.__services:
            if service.name == name:
                return service

    @classmethod
    def process_parameters(cls, kwargs: dict):
        print('processing')
        print(kwargs)

        parameters = dict()
        for parameter in cls.__parameters:
            value = parameter.get_from(kwargs)
            print(f'get {parameter} from kwargs: {value}')
            if value == Parameter.NotFound:
                print(f'{parameter} not found')
                if parameter.default == Parameter.NotSet and not parameter.allow_default:
                    raise ServiceMessage.PARAM_NO_VALUE(str(parameter))
                else:
                    print(f'{parameter} use default value {parameter.default}')
                    value = parameter.default
            else:
                print(f'{parameter} found in kwargs')
                _, value = parameter.p.run(value)
            parameters[parameter] = value
        return parameters

    @classmethod
    def register(cls, service: 'Service'):
        ServiceDepot.register(service)
        service.init()
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
    def async_user_handler(cls, storage_list: List[ServiceData]):
        pass

    @classmethod
    def async_user(cls, storage: ServiceData):
        pass

    @classmethod
    def async_service(cls, storage: ServiceData):
        pass


class ServiceDepot:
    """服务仓库"""
    services = dict()  # type: Dict[str, Service]

    @classmethod
    def register(cls, service: Service):
        if service.name in cls.services:
            raise ValueError(service.name + '重复')

        cls.services[service.name] = service

    @classmethod
    def get(cls, service_name):
        return cls.services.get(service_name)
