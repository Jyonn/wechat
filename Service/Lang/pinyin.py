from smartify import P

from Base.lines import Lines
from Base.tools import Tools
from Service.models import ServiceData, Service, Parameter, ParamDict


@Service.register
class PinyinService(Service):
    name = 'pinyin'
    desc = '汉字转拼音'
    long_desc = Lines(
        "👉pinyin 林俊杰",
        "✅lín jùn jié",
        "当输入单个汉字且是多音字时，默认返回该字的所有拼音",
        "👉pinyin 给",
        "✅gěi/jǐ",
        "可以使用-s或--single来获得单个拼音",
        "👉pinyin -s 给",
        "✅gěi")

    PSingle = Parameter(P(read_name='多音字返回一个拼音').default(), long='single', short='s')

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        if not args:
            return cls.need_help()
        text = args[0]

        heteronym_when_single = not pd.has(cls.PSingle)
        resp = Tools.get(Tools.Pinyin, {
            'text': text,
            'heteronym_when_single': heteronym_when_single
        })
        resp = list(filter(lambda x: x, resp))

        return ' /'[len(text) == 1].join(resp)

    @classmethod
    def init(cls):
        cls.validate(cls.PSingle)
