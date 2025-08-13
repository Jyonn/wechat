import requests
from smartdjango import Code, Error


@Error.register
class VoCError:
    REQUEST = Error("该功能暂时无法使用", code=Code.InternalServerError)
    ERROR = Error("内部错误，功能无法使用", code=Code.InternalServerError)


class VoC:
    @classmethod
    def get(cls, url):
        try:
            with requests.post('https://v.6-79.cn/api/give-me-dl-link', json=dict(url=url, v=2)) as r:
                resp = r.json()
        except Exception:
            raise VoCError.REQUEST
        if resp['code'] == 0:
            return resp['body']
        else:
            raise VoCError.ERROR
