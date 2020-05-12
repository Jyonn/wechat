from django.urls import path

from wechat.views import MessageView, AccessTokenView

urlpatterns = [
    path('message', MessageView.as_view()),
    path('access-token', AccessTokenView.as_view()),
]
