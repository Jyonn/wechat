from SmartDjango import E

from Service.Base.ls import LSService
from Service.models import ServiceData, Service


@E.register(id_processor=E.idp_cls_prefix())
class CDError:
    pass


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
