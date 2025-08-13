from datetime import datetime

from diq import Dictify
from django.db import models
from django.db.models import F
from django.utils.crypto import get_random_string
from smartdjango import Error

from User.validators import UserErrors, MiniUserErrors, MiniUserValidator, UserValidator


class User(models.Model, Dictify):
    vldt = UserValidator

    openid = models.CharField(max_length=vldt.MAX_PHONE_LENGTH, unique=True)

    create_time = models.DateTimeField()

    interaction_times = models.IntegerField(default=1)

    inside_service = models.CharField(max_length=vldt.MAX_INSIDE_SERVICE_LENGTH, null=True, default=None)

    phone = models.CharField(max_length=vldt.MAX_PHONE_LENGTH, null=True, default=None)

    bark = models.CharField(max_length=vldt.MAX_BARK_LENGTH, null=True, default=None)

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

    def set_bark(self, bark):
        self.bark = bark
        self.save()

    @property
    def phone_bind(self):
        return self.phone is not None

    @property
    def bark_bind(self):
        return self.bark is not None

    def require_phone(self):
        if not self.phone:
            raise UserErrors.REQUIRE_PHONE

    def require_bark(self):
        if not self.bark:
            raise UserErrors.REQUIRE_BARK


class MiniUser(models.Model, Dictify):
    vldt = MiniUserValidator

    """小程序用户"""

    user_id = models.CharField(
        max_length=vldt.MAX_USER_ID_LENGTH,
        unique=True,
        validators=[vldt.user_id]
    )

    openid = models.CharField(
        max_length=vldt.MAX_OPENID_LENGTH,
        unique=True,
    )

    avatar = models.CharField(
        max_length=vldt.MAX_AVATAR_LENGTH,
        default=None,
        null=True,
        blank=True,
    )

    nickname = models.CharField(
        max_length=vldt.MAX_NICKNAME_LENGTH,
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
            except Error:
                return user_id

    @classmethod
    def get(cls, user_id):
        try:
            return cls.objects.get(user_id=user_id)
        except cls.DoesNotExist:
            raise MiniUserErrors.NOT_FOUND

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
            raise MiniUserErrors.CREATE(details=err)

    def get_commented_articles(self):
        comments = self.comment_set.values('article__aid').order_by('article__aid').distinct()
        articles = [comment["article__aid"] for comment in comments]
        return articles

    def update(self, avatar, nickname):
        self.avatar = avatar
        self.nickname = nickname
        self.save()

    def d(self):
        return self.dictify('user_id', 'avatar', 'nickname')
