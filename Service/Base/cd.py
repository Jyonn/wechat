from smartdjango import Error, Code

from Base.lines import Lines
from Service.Base.ls import LSService
from Service.models import ServiceData, Service, ParamDict


@Error.register
class CDError:
    SUCCESS = Error("已进入{name}工具箱", code=Code.OK)


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
        raise CDError.SUCCESS(name=terminal.name)
