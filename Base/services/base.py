from SmartDjango import E
from smartify import P

from Base.service import Service, Parameter
from Service.models import ServiceData


@E.register(id_processor=E.idp_cls_prefix())
class BaseServiceError:
    CD_DIR = E("{0}不是目录，无法进入")
    NOT_FOUND = E("没有名为{0}的目录")
    PARENT = E("无法回到上级目录")


@Service.register
class CDService(Service):
    name = 'cd'
    desc = '切换目录'
    long_desc = """暂无详细说明"""

    @classmethod
    def run(cls, directory: Service, storage: ServiceData, parameters: dict, *args):
        paths = args[0] if args else ''
        terminal = LSService.find_path(directory, paths)
        storage.update(dict(service=terminal.name))
        return '已进入{0}目录'.format(terminal.name)


@Service.register
class LSService(Service):
    name = 'ls'
    desc = '查看当前目录'
    long_desc = """暂无详细说明"""

    PLong = Parameter(P(read_name='是否显示完整信息').default(), short='l')

    @staticmethod
    def find_path(current: Service, paths: str):
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
        messages = []
        for child in terminal.get_services():
            if long:
                messages.append('%s\t%s' % (child.name, child.desc))
            else:
                messages.append(child.name)
        return ' \n'[long].join(messages)


LSService.validate(LSService.PLong)
