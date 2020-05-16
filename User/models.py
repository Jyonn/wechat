from datetime import datetime

from SmartDjango import models
from django.db.models import F


class User(models.Model):
    openid = models.CharField(max_length=64, unique=True)

    create_time = models.DateTimeField()

    interaction_times = models.IntegerField(default=1)

    inside_service = models.CharField(max_length=10, null=True, default=None)

    phone = models.CharField(max_length=11, null=True, default=None)

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


class UserP:
    openid, phone = User.P('openid', 'phone')
    openid.process(User.get_or_create).rename('openid', yield_name='user')
