from SmartDjango import Analyse
from django.views import View

from Article.models import ArticleP, Article, CommentP, Comment
from Base.auth import Auth
from Base.weixin import Weixin
from User.models import MiniUser


class ArticleView(View):
    @staticmethod
    @Auth.require_login
    def get(r):
        user = r.user  # type: MiniUser
        return user.article_set.order_by('-pk').all().dict(Article.d_base)

    @staticmethod
    @Analyse.r([ArticleP.title, ArticleP.origin, ArticleP.author])
    @Auth.require_login
    def post(r):
        Weixin.msg_sec_check(r.d.title)
        Weixin.msg_sec_check(r.d.origin)
        Weixin.msg_sec_check(r.d.author)
        return Article.create(r.user, **r.d.dict()).d_create()


class ArticleIDView(View):
    @staticmethod
    @Analyse.r(a=[ArticleP.aid_getter])
    def get(r):
        article = r.d.article
        return article.d()

    @staticmethod
    @Analyse.r(a=[ArticleP.aid_getter])
    @Auth.require_login
    def delete(r):
        article = r.d.article
        article.assert_belongs_to(r.user)
        article.remove()


class CommentView(View):
    @staticmethod
    @Analyse.r(b=[CommentP.content, CommentP.reply_to_getter], a=[ArticleP.aid_getter])
    @Auth.require_login
    def post(r):
        article = r.d.article  # type: Article
        content = r.d.content
        reply_to = r.d.reply_to  # type: Comment

        Weixin.msg_sec_check(content)

        if reply_to:
            return reply_to.reply(r.user, content).d()
        return article.comment(r.user, content).d()


class CommentIDView(View):
    @staticmethod
    @Analyse.r(a=[ArticleP.aid_getter, CommentP.cid_getter])
    @Auth.require_login
    def post(r):
        article = r.d.article
        comment = r.d.comment
        user = r.user

        comment.assert_belongs_to(article)
        comment.assert_belongs_to(user)

        comment.remove()
