from smartdjango import Error, Code


@Error.register
class UserErrors:
    REQUIRE_PHONE = Error("该工具需要绑定手机，详见bind命令", code=Code.Unauthorized)
    REQUIRE_BARK = Error("该工具需要绑定Bark，详见bark命令", code=Code.BadRequest)


@Error.register
class MiniUserErrors:
    NOT_FOUND = Error("找不到小程序用户", code=Code.NotFound)
    CREATE = Error("创建小程序用户失败", code=Code.InternalServerError)
    USER_ID_TOO_SHORT = Error("用户ID长度不能小于{length}", code=Code.BadRequest)


class UserValidator:
    MAX_OPENID_LENGTH = 64
    MAX_INSIDE_SERVICE_LENGTH = 10
    MAX_PHONE_LENGTH = 20
    MAX_BARK_LENGTH = 100


class MiniUserValidator:
    MAX_USER_ID_LENGTH = 6
    MIN_USER_ID_LENGTH = 6
    MAX_OPENID_LENGTH = 64
    MAX_AVATAR_LENGTH = 512
    MAX_NICKNAME_LENGTH = 64

    @classmethod
    def user_id(cls, user_id):
        if len(user_id) < cls.MIN_USER_ID_LENGTH:
            raise MiniUserErrors.USER_ID_TOO_SHORT(length=cls.MIN_USER_ID_LENGTH)
