from django.urls import path, include

from wechat.views import MessageView, AccessTokenView, TestView, ServiceView, ErrorView

urlpatterns = [
    path('message', MessageView.as_view()),
    path('access-token', AccessTokenView.as_view()),
    path('test', TestView.as_view()),
    path('error', ErrorView.as_view()),
    path('service', ServiceView.as_view()),
    path('user/', include('User.urls')),
    path('article/', include('Article.urls')),
]
