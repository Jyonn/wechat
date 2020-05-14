from SmartDjango import E
from smartify import P

from Base.common import ROOT_NAME
from Base.service import Service, Parameter, ServiceDepot
from Service.models import ServiceData


@E.register(id_processor=E.idp_cls_prefix())
class BaseServiceError:
    CD_DIR = E("{0}不是工具箱，无法进入")
    NOT_FOUND = E("没有名为{0}的工具箱")
    PARENT = E("没有更大的工具箱啦")


@Service.register
class CommandLineService(Service):
    name = 'cmd'
    desc = '消息回复的命令行操作'

    PShow = Parameter(P(read_name='显示命令行').default(), long='show')
    PHide = Parameter(P(read_name='隐藏命令行').default(), long='hide')

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        if cls.PShow.set(parameters):
            storage.update(dict(hide=False))
        if cls.PHide.set(parameters):
            storage.update(dict(hide=True))


CommandLineService.validate(CommandLineService.PShow, CommandLineService.PHide)


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


LSService.validate(LSService.PLong)
