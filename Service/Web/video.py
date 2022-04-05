from Base.lines import Lines
from Base.voc import VoC
from Service.models import ServiceData, Service, ParamDict


@Service.register
class VideoService(Service):
    name = 'video'
    desc = '视频解析'
    long_desc = Lines(
        '支持新片场、抖音、二更、开眼等多家视频网站解析',
        '👉video https://www.xinpianchang.com/a11609495'
    )

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        if not args:
            return cls.need_help()

        resp = VoC.get(url=args[0])
        messages = [
            '视频名称：' + resp['video_info']['title'],
            '<a href="{}">视频封面</a>'.format(resp['video_info']['cover'])
        ]
        for option in resp['more_options']:
            messages.append('<a href="{}">{}</a>'.format(option['url'], option['quality']))
        return '\n'.join(messages)
