from typing import Optional

from SmartDjango import E

from Base.parser import Parser
from Base.service import ServiceDepot, Service
from Base.services.root import LanguageService
from Service.models import ServiceData
from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class HandlerError:
    NOT_FOUND = E("找不到{0}命令")


@Service.register
class RootService(Service):
    name = 'root'
    desc = '根目录'
    long_desc = '暂无介绍'

    as_dir = True


RootService.contains(LanguageService)


class MessageHandler:
    @classmethod
    def get_directory(cls, user: User):
        data = ServiceData.get_or_create('cd', user).classify()
        service = ServiceDepot.get(data.service or 'root')
        return service

    def __init__(self, user: User, command: Optional[str]):
        # command = message.content  # type: # Optional[str]
        service = None  # type: Optional[Service]
        if user.inside_service:
            service_name = user.inside_service
            service = ServiceDepot.get(service_name)
            if not service:
                user.inside(None)
                raise HandlerError.NOT_FOUND(service_name)

        if not service:
            splits = command.split(' ', maxsplit=1)
            service_name = splits[0]
            if len(splits) == 2:
                command = splits[1]
            else:
                command = ''

            service = ServiceDepot.get(service_name)
            if not service:
                raise HandlerError.NOT_FOUND(service_name)

        storage = ServiceData.get_or_create(service, user)
        parameters = storage.fetch_parameters()
        args, kwargs = Parser.parse(command)
        kwargs.update(parameters)
        parameters = service.process_parameters(kwargs)
        if '--inside' in kwargs:
            user.inside(service.name)

        if '--quit' in kwargs:
            user.inside(None)
            self.message = '已退出%s' % service.name
        else:
            directory = self.get_directory(user)
            self.message = service.work(directory, storage, parameters, *args)
