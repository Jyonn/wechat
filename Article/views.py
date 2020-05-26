from SmartDjango import Analyse
from django.views import View

from Article.models import ArticleP, Article, CommentP, Comment
from Base.auth import Auth


class ArticleView(View):
    @staticmethod
    @Analyse.r([ArticleP.title])
    @Auth.require_login
    def post(r):
        return Article.create(r.user, r.d.title).d_create()


class CommentView(View):
    @staticmethod
    @Analyse.r([ArticleP.aid_getter, CommentP.content, CommentP.reply_to_getter])
    @Auth.require_login
    def post(r):
        article = r.d.artcile  # type: Article
        content = r.d.content
        reply_to = r.d.reply_to  # type: Comment

        if reply_to:
            return reply_to.reply(r.user, content).d()
        return article.comment(r.user, content).d()
