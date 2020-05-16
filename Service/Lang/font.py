from Base.tools import Tools
from Service.models import ServiceData, Service


@Service.register
class FontService(Service):
    name = 'font'
    desc = '英文数字转花体字'
    long_desc = '若句子中存在空格，需加引号\n' \
                'font "this is a sentence with space"\n' \
                'font TheSentenceWithoutSpace\n'

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        if not args:
            return cls.need_help()
        resp = Tools.get(Tools.FlowerFont, {"sentence": args[0]})
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
