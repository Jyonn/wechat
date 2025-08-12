from django.views import View
from smartdjango import analyse

from Base.auth import Auth
from Base.weixin import Weixin
from User.models import MiniUser
from User.params import MiniUserParams


class CodeView(View):
    @analyse.query('code')
    def get(self, request):
        code = request.query.code

        data = Weixin.code2session(code)
        openid = data['openid']
        session_key = data['session_key']

        user = MiniUser.get_or_create(openid)
        return Auth.get_login_token(user, session_key=session_key)


class UserView(View):
    @analyse.json('encrypted_data', 'iv')
    @Auth.require_login
    def put(self, request):
        user = request.user  # type: MiniUser
        session_key = request.session_key

        encrypted_data = request.json.encrypted_data
        iv = request.json.iv

        data = Weixin.decrypt(encrypted_data, iv, session_key)

        avatar = data['avatarUrl']
        nickname = data['nickName']
        MiniUserParams.avatar.clean(avatar)
        MiniUserParams.nickname.clean(nickname)

        user.update(avatar, nickname)

        return user.d()
