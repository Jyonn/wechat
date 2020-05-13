import requests
from SmartDjango import E


@E.register(id_processor=E.idp_cls_prefix())
class ToolsError:
    REQUEST = E("该功能暂时无法使用")
    ERROR = E("内部错误，功能无法使用")


class Tools:
    FlowerFont = '/language/unicode-font'
    Pinyin = '/language/character-to-pinyin'

    @classmethod
    def get(cls, url, data=None):
        data = data or {}
        try:
            with requests.post('https://tools.6-79.cn/v1' + url, json=data) as r:
                resp = r.json()
        except Exception:
            raise ToolsError.REQUEST
        if resp['code'] == 0:
            return resp['body']
        else:
            raise ToolsError.ERROR
