from django.urls import path

from Article.views import ArticleView, CommentView, CommentIDView, ArticleIDView

urlpatterns = [
    path('', ArticleView.as_view()),
    path('<str:aid>', ArticleIDView.as_view()),
    path('<str:aid>/comment', CommentView.as_view()),
    path('<str:aid>/comment/<str:cid>', CommentIDView.as_view()),
]
