import requests
from smartdjango import Code, Error


@Error.register
class ToolsErrors:
    REQUEST = Error("该功能暂时无法使用", code=Code.InternalServerError)
    ERROR = Error("内部错误，功能无法使用", code=Code.InternalServerError)


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
            raise ToolsErrors.REQUEST
        if resp['code'] == 0:
            return resp['body']
        raise ToolsErrors.ERROR
