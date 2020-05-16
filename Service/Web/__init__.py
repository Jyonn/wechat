from Service.Web.watch import WatchService
from Service.models import Service


@Service.register
class WebService(Service):
    name = 'web'
    desc = '网络工具箱'
    long_desc = '包含网页变化监控等工具'

    as_dir = True

    @classmethod
    def init(cls):
        cls.contains(WatchService)
