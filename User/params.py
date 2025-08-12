from smartdjango import Params, Validator

from User.models import User, MiniUser


class UserParams(metaclass=Params):
    model_class = User

    openid: Validator
    phone: Validator
    bark: Validator

    user_getter = Validator('openid', final_name='user').to(User.get_or_create)


class MiniUserParams(metaclass=Params):
    model_class = MiniUser

    avatar: Validator
    nickname: Validator
