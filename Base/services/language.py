from smartify import P

from Base.service import Service, Parameter
from Base.tools import Tools
from Service.models import ServiceData


@Service.register
class FlowerFontService(Service):
    name = 'font'
    desc = '花体英文数字转换'

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


@Service.register
class PinyinService(Service):
    name = 'pinyin'
    desc = '汉字转拼音'
    long_desc = "如获得林俊杰的拼音\n" \
                "pinyin 林俊杰\n" \
                "> lín jùn jié\n" \
                "当输入单个汉字且是多音字时，默认返回该字的所有拼音\n" \
                "pinyin 给\n" \
                "> gěi/jǐ\n" \
                "可以使用-s或--single来获得单个拼音\n" \
                "pinyin -s 给\n" \
                "> gěi"

    PSingle = Parameter(P(read_name='多音字返回一个拼音').default(), long='single', short='s')

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, parameters: dict, *args):
        text = args[0] if args else ''

        heteronym_when_single = not cls.PSingle.set(parameters)
        print(parameters)
        resp = Tools.get(Tools.Pinyin, {
            'text': text,
            'heteronym_when_single': heteronym_when_single
        })
        resp = list(filter(lambda x: x, resp))

        return ' /'[len(text) == 1].join(resp)

    @classmethod
    def init(cls):
        cls.validate(cls.PSingle)
