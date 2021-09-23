from datetime import datetime

from SmartDjango import models, E
from django.db.models import F
from django.utils.crypto import get_random_string


@E.register(id_processor=E.idp_cls_prefix())
class UserError:
    REQUIRE_PHONE = E("该工具需要绑定手机，详见bind命令")


class User(models.Model):
    openid = models.CharField(max_length=64, unique=True)

    create_time = models.DateTimeField()

    interaction_times = models.IntegerField(default=1)

    inside_service = models.CharField(max_length=10, null=True, default=None)

    phone = models.CharField(max_length=20, null=True, default=None)

    @classmethod
    def get_or_create(cls, openid):
        try:
            user = cls.objects.get(openid=openid)
            user.interact()
            return user
        except cls.DoesNotExist:
            return cls.objects.create(openid=openid, create_time=datetime.now())

    def interact(self):
        self.interaction_times = F('interaction_times') + 1
        self.save()
        self.refresh_from_db()

    def inside(self, service):
        self.inside_service = service
        self.save()

    def set_phone(self, phone):
        self.phone = phone
        self.save()

    @property
    def phone_bind(self):
        return self.phone is not None

    def require_phone(self):
        if not self.phone:
            raise UserError.REQUIRE_PHONE


class UserP:
    openid, phone = User.P('openid', 'phone')
    openid.process(User.get_or_create).rename('openid', yield_name='user')


@E.register(id_processor=E.idp_cls_prefix())
class MiniUserError:
    NOT_FOUND = E("找不到小程序用户")
    CREATE = E("创建小程序用户失败")


class MiniUser(models.Model):
    """小程序用户"""

    user_id = models.CharField(
        max_length=6,
        min_length=6,
        unique=True,
    )

    openid = models.CharField(
        max_length=64,
        unique=True,
    )

    avatar = models.CharField(
        max_length=512,
        default=None,
        null=True,
        blank=True,
    )

    nickname = models.CharField(
        max_length=64,
        default=None,
        null=True,
        blank=True,
    )

    @classmethod
    def get_unique_id(cls):
        while True:
            user_id = get_random_string(length=6)
            try:
                cls.get(user_id)
            except E:
                return user_id

    @classmethod
    def get(cls, user_id):
        try:
            return cls.objects.get(user_id=user_id)
        except cls.DoesNotExist:
            raise MiniUserError.NOT_FOUND

    @classmethod
    def get_or_create(cls, openid):
        try:
            return cls.objects.get(openid=openid)
        except cls.DoesNotExist:
            pass

        try:
            return cls.objects.create(
                openid=openid,
                user_id=cls.get_unique_id(),
            )
        except Exception as err:
            raise MiniUserError.CREATE(debug_message=err)

    def get_commented_articles(self):
        comments = self.comment_set.values('article__aid').order_by('article__aid').distinct()
        articles = [comment["article__aid"] for comment in comments]
        return articles

    def update(self, avatar, nickname):
        self.validator(locals())
        self.avatar = avatar
        self.nickname = nickname
        self.save()

    def d(self):
        return self.dictify('user_id', 'avatar', 'nickname')
