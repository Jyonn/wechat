from SmartDjango import E

from Base.common import msg_idp
from Base.lines import Lines
from Service.Base.ls import LSService
from Service.models import ServiceData, Service, ParamDict


@E.register(id_processor=msg_idp)
class CDError:
    SUCCESS = E("已进入{}工具箱")


@Service.register
class CDService(Service):
    name = 'cd'
    desc = '切换工具箱'
    long_desc = Lines(
        '👉cd lang',
        '👉cd ../web')

    @classmethod
    def run(cls, directory: Service, storage: ServiceData, pd: ParamDict, *args):
        paths = args[0] if args else ''
        terminal = LSService.find_path(directory, paths)
        storage.update(dict(service=terminal.name))
        raise CDError.SUCCESS(terminal.name)
