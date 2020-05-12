from datetime import datetime

from SmartDjango import models
from django.db.models import F


class User(models.Model):
    openid = models.CharField(max_length=64, unique=True)

    create_time = models.DateTimeField()

    interaction_times = models.IntegerField(default=1)

    @classmethod
    def create(cls, openid):
        try:
            user = cls.objects.get(openid=openid)
            user.interact()
            return user
        except cls.DoesNotExist:
            return cls.objects.create(openid=openid, create_time=datetime.now())

    def interact(self):
        self.interaction_times = F('interaction_times') + 1
        self.save()


class UserP:
    openid, = User.P('openid')
    openid.process(User.create).rename('openid', yield_name='user')
