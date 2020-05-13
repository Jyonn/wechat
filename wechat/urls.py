from django.urls import path

from wechat.views import MessageView, AccessTokenView, TestView

urlpatterns = [
    path('message', MessageView.as_view()),
    path('access-token', AccessTokenView.as_view()),
    path('test', TestView.as_view()),
]
