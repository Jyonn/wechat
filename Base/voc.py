import requests
from SmartDjango import E


@E.register(id_processor=E.idp_cls_prefix())
class VoCError:
    REQUEST = E("该功能暂时无法使用")
    ERROR = E("内部错误，功能无法使用")


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
