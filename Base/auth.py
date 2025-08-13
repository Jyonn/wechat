from functools import wraps

from django.http import HttpRequest
from smartdjango import Error, Code, analyse
from wechatpy.utils import check_signature

from Base.common import WX_TOKEN, DEV_MODE
from Base.crypto import Crypto
from Base.jtoken import JWT
from User.models import MiniUser


@Error.register
class AuthErrors:
    LOCAL = Error("只允许本地调试", code=Code.Forbidden)
    TOKEN_MISS_PARAM = Error("缺少参数: {param}", code=Code.BadRequest)
    REQUIRE_LOGIN = Error("需要登录", code=Code.Unauthorized)


class Auth:
    @staticmethod
    def validate_token(request):
        jwt_str = request.META.get('HTTP_TOKEN')
        if not jwt_str:
            raise AuthErrors.REQUIRE_LOGIN

        return JWT.decrypt(jwt_str)

    @staticmethod
    def get_login_token(user: MiniUser, session_key):
        if DEV_MODE:
            encrypt_session_key = session_key
        else:
            encrypt_session_key = Crypto.AES.encrypt(session_key)
        token, dict_ = JWT.encrypt(dict(
            user_id=user.user_id,
            session_key=encrypt_session_key,
        ))
        dict_['token'] = token
        dict_['user'] = user.d()
        return dict_

    @classmethod
    def _extract_user(cls, request):
        request.user = None

        dict_ = cls.validate_token(request)
        user_id = dict_.get('user_id')
        if not user_id:
            raise AuthErrors.TOKEN_MISS_PARAM(param='user_id')
        session_key = dict_.get("session_key")
        if not session_key:
            raise AuthErrors.TOKEN_MISS_PARAM(param='session_key')

        if DEV_MODE:
            request.session_key = session_key
        else:
            request.session_key = Crypto.AES.decrypt(session_key)
        request.user = MiniUser.get(user_id)

    @classmethod
    def require_login(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = analyse.get_request(*args)
            cls._extract_user(request)
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def wechat(func):
        def wrapper(*args, **kwargs):
            request = analyse.get_request(*args)
            try:
                check_signature(
                    token=WX_TOKEN,
                    signature=request.data.signature,
                    timestamp=request.data.timestamp,
                    nonce=request.data.nonce,
                    # **r.d.dict('signature', 'timestamp', 'nonce')
                )
            except Exception as _:
                return 0
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def only_localhost(func):
        def wrapper(*args, **kwargs):
            request = analyse.get_request(*args)
            host = request.get_host()
            if ':' in host:
                host = host[:host.index(':')]
            if host == 'localhost':
                return func(*args, **kwargs)
            raise AuthErrors.LOCAL
        return wrapper
