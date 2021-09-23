from typing import Optional

from SmartDjango import E

from Base.parser import Parser
from Base.root import ROOT_NAME
from Service.models import ServiceData, ServiceDepot, ParamDict, Service
from User.models import User
from Service.Base import BaseService
from Service.Lang import LanguageService
from Service.Web import WebService


@E.register(id_processor=E.idp_cls_prefix())
class HandlerError:
    NOT_FOUND = E("找不到名为{0}的杰作")


@Service.register
class RootService(Service):
    name = ROOT_NAME
    desc = '杰作箱'
    long_desc = '按树状结构呈现，可使用ls/cd等杰作获取内部信息'

    as_dir = True

    @classmethod
    def init(cls):
        cls.contains(LanguageService, BaseService, WebService)


class MessageHandler:
    @classmethod
    def get_directory(cls, user: User):
        data = ServiceData.get_or_create('cd', user).classify()
        service = ServiceDepot.get(data.service or ROOT_NAME)
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
        parameters = ParamDict(parameters)
        if '--inline' in kwargs:
            user.inside(service.name)
            self.message = '已进入%s命令，退出请输入--quit' % service.name
            return

        directory = self.get_directory(user)  # type: Service
        # console_line = directory.get_console_line() + service.name + '\n'
        # console_line = LNormalBoldItalic.translate(console_line)
        if '--quit' in kwargs:
            user.inside(None)
            self.message = '已退出%s命令' % service.name
        else:
            try:
                self.message = service.work(directory, storage, parameters, *args) or ''
            except Exception as e:
                self.message = str(e)

        # if not self.is_cmd_hide(user):
        #     self.message = console_line + self.message
