from Base.service import Service
from Base.tools import Tools
from Service.models import ServiceData


@Service.register
class FlowerFontService(Service):
    name = 'font'
    desc = '花体英文数字转换'
    long_desc = ''

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        resp = Tools.get(Tools.FlowerFont, {"sentence": args[0] if args else ''})
        messages = []
        if not resp['supported']:
            messages.append('暂无完全支持的花字体')
        else:
            messages.append('以下为完全支持的花字体')
            for font in resp['supported']:
                messages.append(font['sentence'])

        if resp['unsupported']:
            messages.append('下方有部分字符无法转换')
            for font in resp['unsupported']:
                messages.append(font['sentence'])
        return '\n'.join(messages)
