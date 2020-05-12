from SmartDjango import E

from Base.service import Service


@E.register(id_processor=E.idp_cls_prefix())
class BaseServiceError:
    CD_DIR = E("{0}不是目录，无法进入")


@Service.register
class CDService(Service):
    name = 'cd'
    desc = '切换目录'
    long_desc = """暂无详细说明"""

    @classmethod
    def run(cls, name, *args, service: 'Service', **kwargs):
        cd_service = service.get(name)
        if not cd_service.as_dir:
            raise BaseServiceError.CD_DIR(cd_service.name)
        return '已进入{0}目录'.format(cd_service.name)
