from functools import wraps

from SmartDjango import E
from django.http import HttpRequest
from wechatpy.utils import check_signature

from Base.common import WX_TOKEN, DEV_MODE
from Base.crypto import Crypto
from Base.jtoken import JWT
from User.models import MiniUser


@E.register(id_processor=E.idp_cls_prefix())
class AuthError:
    LOCAL = E("只允许本地调试")
    TOKEN_MISS_PARAM = E("缺少参数{0}")
    REQUIRE_LOGIN = E("需要登录")


class Auth:
    @staticmethod
    def validate_token(request):
        jwt_str = request.META.get('HTTP_TOKEN')
        # jwt_str = request.COOKIES['token']
        if not jwt_str:
            raise AuthError.REQUIRE_LOGIN

        return JWT.decrypt(jwt_str)

    @staticmethod
    def get_login_token(user: MiniUser, session_key):
        if DEV_MODE:
            encrypt_session_key = session_key
        else:
            encrypt_session_key = Crypto.AES.encrypt(session_key)
        token, _dict = JWT.encrypt(dict(
            user_id=user.user_id,
            session_key=encrypt_session_key,
        ))
        _dict['token'] = token
        _dict['user'] = user.d()
        return _dict

    @classmethod
    def _extract_user(cls, r):
        r.user = None

        dict_ = cls.validate_token(r)
        user_id = dict_.get('user_id')
        if not user_id:
            raise AuthError.TOKEN_MISS_PARAM('user_id')
        session_key = dict_.get("session_key")
        if not session_key:
            raise AuthError.TOKEN_MISS_PARAM('session_key')

        if DEV_MODE:
            r.session_key = session_key
        else:
            r.session_key = Crypto.AES.decrypt(session_key)
        r.user = MiniUser.get(user_id)

    @classmethod
    def require_login(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            return func(r, *args, **kwargs)

        return wrapper

    @staticmethod
    def wechat(func):
        def wrapper(r, *args, **kwargs):
            try:
                check_signature(
                    token=WX_TOKEN,
                    signature=r.d.signature,
                    timestamp=r.d.timestamp,
                    nonce=r.d.nonce,
                    # **r.d.dict('signature', 'timestamp', 'nonce')
                )
            except Exception as e:
                return 0
            return func(r, *args, **kwargs)

        return wrapper

    @staticmethod
    def only_localhost(func):
        def wrapper(r: HttpRequest, *args, **kwargs):
            host = r.get_host()
            if ':' in host:
                host = host[:host.index(':')]
            if host == 'localhost':
                return func(r, *args, **kwargs)
            raise AuthError.LOCAL
        return wrapper
