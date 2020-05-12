from Base.service import Service
from Base.services.language import FlowerFontService


@Service.register
class LanguageService(Service):
    name = 'lang'
    desc = '语言类'
    long_desc = '包含花体字等功能'

    as_dir = True
    services = [FlowerFontService]
