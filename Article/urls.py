from django.urls import path

from Article.views import ArticleView, CommentView

urlpatterns = [
    path('', ArticleView.as_view()),
    path('<str:aid>/comment', CommentView.as_view()),
]
