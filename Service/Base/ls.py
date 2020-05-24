from SmartDjango import E
from smartify import P

from Base.para import Para
from Base.root import ROOT_NAME
from Service.models import ServiceData, Service, Parameter, ServiceDepot


@E.register(id_processor=E.idp_cls_prefix())
class LSError:
    CD_DIR = E("{0}不是工具箱，无法进入")
    NOT_FOUND = E("没有名为{0}的工具箱")
    PARENT = E("没有更大的工具箱啦")


@Service.register
class LSService(Service):
    name = 'ls'
    desc = '查看工具箱'
    long_desc = Para(
        '👉ls lang',
        '👉ls ../web')

    PLong = Parameter(P(read_name='是否显示完整信息').default(), short='l')

    @staticmethod
    def find_path(current: Service, paths: str):
        if paths and paths[0] == '/':
            current = ServiceDepot.get(ROOT_NAME)
        paths = paths.split('/')
        for path in paths:
            if path == '..':
                if not current.parent:
                    raise LSError.PARENT
                current = current.parent
            elif path != '.' and path != '':
                current = current.get(path)
                if not current:
                    raise LSError.NOT_FOUND(path)
                if not current.as_dir:
                    raise LSError.CD_DIR(current.name)
        return current

    @classmethod
    def init(cls):
        cls.validate(cls.PLong)

    @classmethod
    def run(cls, directory: Service, storage: ServiceData, parameters: dict, *args):
        paths = args[0] if args else ''
        terminal = cls.find_path(directory, paths)

        long = cls.PLong.is_set_in(parameters)
        messages = ['%s中拥有以下工具：' % terminal.name]
        for child in terminal.get_services():
            name = child.name + ['（工具）', '（工具箱）'][child.as_dir]
            if long:
                messages.append('%s\t%s' % (name, child.desc))
            else:
                messages.append(name)
        return '\n'.join(messages)
