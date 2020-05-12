from django.http import HttpRequest
from django.views import View


class MessageView(View):
    @staticmethod
    def get(r: HttpRequest):
        print(r.GET.dict())
