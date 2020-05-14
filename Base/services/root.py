from Base.service import Service
from Base.services.base import LSService, CDService, CommandLineService
from Base.services.language import FlowerFontService, PinyinService


@Service.register
class LanguageService(Service):
    name = 'lang'
    desc = '语言工具箱'
    long_desc = '包含花体英文数字转换、汉字转拼音等工具'

    as_dir = True


LanguageService.contains(FlowerFontService, PinyinService)


@Service.register
class BaseService(Service):
    name = 'base'
    desc = '基础工具箱'
    long_desc = '包含查看当前工具箱、切换工具箱等工具'

    as_dir = True


BaseService.contains(LSService, CDService)
