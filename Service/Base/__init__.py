from Service.Base.bind import BindPhoneService
from Service.Base.cd import CDService
from Service.Base.ls import LSService
from Service.models import Service


@Service.register
class BaseService(Service):
    name = 'base'
    desc = '基础工具箱'
    long_desc = '包含查看当前工具箱、切换工具箱等工具'

    as_dir = True

    @classmethod
    def init(cls):
        cls.contains(LSService, CDService, BindPhoneService)
