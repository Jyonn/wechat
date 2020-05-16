from smartify import P

from Base.tools import Tools
from Service.models import ServiceData, Service, Parameter


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
        if not args:
            return cls.need_help()
        text = args[0]

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
