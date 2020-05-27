from SmartDjango import Analyse, NetPacker
from django.views import View

from Base.auth import Auth
from Base.weixin import Weixin
from User.models import MiniUser


class CodeView(View):
    @staticmethod
    @Analyse.r(q=['code'])
    def get(r):
        code = r.d.code

        data = Weixin.code2session(code)
        openid = data['openid']
        session_key = data['session_key']

        user = MiniUser.get_or_create(openid)
        return Auth.get_login_token(user, session_key=session_key)


class UserView(View):
    @staticmethod
    @Analyse.r(['encrypted_data', 'iv'])
    @Auth.require_login
    def put(r):
        user = r.user  # type: MiniUser
        session_key = r.session_key

        encrypted_data = r.d.encrypted_data
        iv = r.d.iv

        data = Weixin.decrypt(encrypted_data, iv, session_key)

        avatar = data['avatarUrl']
        nickname = data['nickName']
        user.update(avatar, nickname)

        return user.d()
