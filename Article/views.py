from SmartDjango import Analyse
from django.views import View

from Article.models import ArticleP, Article, CommentP, Comment
from Base.auth import Auth


class ArticleView(View):
    @staticmethod
    @Analyse.r(q=[ArticleP.aid_getter])
    def get(r):
        article = r.d.article
        return article.d()

    @staticmethod
    @Analyse.r([ArticleP.title, ArticleP.origin, ArticleP.author])
    @Auth.require_login
    def post(r):
        return Article.create(r.user, **r.d.dict()).d_create()


class CommentView(View):
    @staticmethod
    @Analyse.r(b=[CommentP.content, CommentP.reply_to_getter], a=[ArticleP.aid_getter])
    @Auth.require_login
    def post(r):
        article = r.d.article  # type: Article
        content = r.d.content
        reply_to = r.d.reply_to  # type: Comment

        if reply_to:
            return reply_to.reply(r.user, content).d()
        return article.comment(r.user, content).d()
