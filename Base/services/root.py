from Base.service import Service
from Base.services.base import LSService, CDService, CommandLineService
from Base.services.language import FlowerFontService, PinyinService


@Service.register
class LanguageService(Service):
    name = 'lang'
    desc = '语言功能包'
    long_desc = '包含花体字等功能'

    as_dir = True


LanguageService.contains(FlowerFontService, PinyinService)


@Service.register
class BaseService(Service):
    name = 'base'
    desc = '基础功能包'
    long_desc = '包含查看当前目录、切换目录等功能'

    as_dir = True


BaseService.contains(LSService, CDService, CommandLineService)
