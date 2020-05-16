from Service.Lang.font import FontService
from Service.Lang.pinyin import PinyinService
from Service.models import Service


@Service.register
class LanguageService(Service):
    name = 'lang'
    desc = '语言工具箱'
    long_desc = '包含花体英文数字转换、汉字转拼音等工具'

    as_dir = True

    @classmethod
    def init(cls):
        cls.contains(FontService, PinyinService)
