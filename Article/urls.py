from django.urls import path

from Article.views import ArticleView, CommentView, ArticleIDView

urlpatterns = [
    path('', ArticleView.as_view()),
    path('<str:aid>', ArticleIDView.as_view()),
    path('<str:aid>/comment', CommentView.as_view()),
]
