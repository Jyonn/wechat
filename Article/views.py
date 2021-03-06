from SmartDjango import Analyse
from django.views import View
from smartify import P

from Article.models import ArticleP, Article, CommentP, Comment
from Base.auth import Auth
from Base.weixin import Weixin
from User.models import MiniUser


class ArticleView(View):
    @staticmethod
    @Analyse.r(q=[P('role', '角色').default('owner')])
    @Auth.require_login
    def get(r):
        user = r.user  # type: MiniUser
        if r.d.role == 'owner':
            return user.article_set.order_by('-pk').all().dict(Article.d_base)
        else:
            return list(map(lambda aid: Article.get(aid).d_base(), user.get_commented_articles()))

    @staticmethod
    @Analyse.r([
        ArticleP.title,
        ArticleP.origin,
        ArticleP.author,
        ArticleP.self_product,
        ArticleP.require_review,
        ArticleP.allow_open_reply,
    ])
    @Auth.require_login
    def post(r):
        Weixin.msg_sec_check(r.d.title)
        Weixin.msg_sec_check(r.d.origin)
        Weixin.msg_sec_check(r.d.author)
        return Article.create(r.user, **r.d.dict()).d_create()


class ArticleIDView(View):
    @staticmethod
    @Analyse.r(a=[ArticleP.aid_getter])
    @Auth.require_login
    def get(r):
        article = r.d.article
        d = article.d(r.user)
        return d

    @staticmethod
    @Analyse.r(a=[ArticleP.aid_getter], b=[ArticleP.title, ArticleP.origin, ArticleP.author])
    @Auth.require_login
    def put(r):
        Weixin.msg_sec_check(r.d.title)
        Weixin.msg_sec_check(r.d.origin)
        Weixin.msg_sec_check(r.d.author)
        article = r.d.article
        article.update(**r.d.dict('title', 'origin', 'author'))

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
    def delete(r):
        article = r.d.article
        comment = r.d.comment
        user = r.user

        comment.assert_belongs_to(article)
        comment.assert_belongs_to(user)

        comment.remove()
