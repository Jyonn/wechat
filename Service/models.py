import json

from SmartDjango import models
from django.db.models import F


class ServiceData(models.Model):
    service = models.CharField(
        max_length=10,
    )

    user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
    )

    data = models.TextField(
        null=True,
        default=None,
    )

    interact_times = models.IntegerField(default=1)

    @classmethod
    def get_or_create(cls, service, user):
        try:
            service_data = cls.objects.get(service=service, user=user)
            service_data.interact()
            return service_data
        except cls.DoesNotExist:
            return cls.objects.create(service=service, user=user)

    def interact(self):
        self.interaction_times = F('interaction_times') + 1
        self.save()
        self.refresh_from_db()

    def jsonify(self):
        data = self.data or '{}'
        return json.loads(data)

    def update(self, data):
        self.data = json.dumps(data, ensure_ascii=False)
        self.save()
