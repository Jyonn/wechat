from Service.Web.boc import BOCService
# from Service.Web.sms import SMSService
from Service.Web.video import VideoService
from Service.Web.watch import WatchService
from Service.models import Service


@Service.register
class WebService(Service):
    name = 'web'
    desc = '网络工具箱'
    long_desc = '包含网页变化监控、视频解析等工具'

    as_dir = True

    @classmethod
    def init(cls):
        cls.contains(WatchService, BOCService, VideoService)
