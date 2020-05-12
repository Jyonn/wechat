from wechatpy.utils import check_signature

from Base.common import WX_TOKEN


class Auth:
    @staticmethod
    def wechat(func):
        def wrapper(r, *args, **kwargs):
            try:
                check_signature(token=WX_TOKEN, **r.d.dict('signature', 'timestamp', 'nonce'))
            except Exception:
                return 0
            return func(r, *args, **kwargs)

        return wrapper
