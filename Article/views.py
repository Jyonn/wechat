from django.views import View
from smartdjango import Validator, analyse, OK

from Article.models import Article, Comment
from Article.params import ArticleParams, CommentParams
from Base.auth import Auth
from Base.weixin import Weixin
from User.models import MiniUser


class ArticleView(View):
    @analyse.query(Validator('role', '角色').default('owner').null())
    @Auth.require_login
    def get(self, request):
        user = request.user  # type: MiniUser
        if request.query.role == 'owner':
            articles = user.article_set.order_by('-pk').all()
            return [article.d_base() for article in articles]

        return list(map(lambda aid: Article.get(aid).d_base(), user.get_commented_articles()))

    @analyse.json(
        ArticleParams.title,
        ArticleParams.origin,
        ArticleParams.author,
        ArticleParams.self_product,
        ArticleParams.require_review,
        ArticleParams.allow_open_reply,
    )
    @Auth.require_login
    def post(self, request):
        Weixin.msg_sec_check(request.json.title)
        Weixin.msg_sec_check(request.json.origin)
        Weixin.msg_sec_check(request.json.author)
        return Article.create(request.user, **request.d.dict()).d_create()


class ArticleIDView(View):
    @analyse.argument(ArticleParams.aid_getter)
    @Auth.require_login
    def get(self, request, **kwargs):
        article = request.d.article
        return article.d(request.user)

    @analyse.argument(ArticleParams.aid_getter)
    @analyse.json(ArticleParams.title, ArticleParams.origin, ArticleParams.author)
    @Auth.require_login
    def put(self, request, **kwargs):
        Weixin.msg_sec_check(request.jsopn.title)
        Weixin.msg_sec_check(request.json.origin)
        Weixin.msg_sec_check(request.json.author)
        article = request.argument.article
        article.update(
            title=request.json.title,
            origin=request.json.origin,
            author=request.json.author,
        )
        return OK

    @analyse.argument(ArticleParams.aid_getter)
    @Auth.require_login
    def delete(self, request, **kwargs):
        article = request.argument.article
        article.assert_belongs_to(request.user)
        article.remove()
        return OK


class CommentView(View):
    @analyse.json(CommentParams.content, CommentParams.reply_to_getter)
    @analyse.argument(ArticleParams.aid_getter)
    @Auth.require_login
    def post(self, request, **kwargs):
        article = request.argument.article  # type: Article
        content = request.json.content
        reply_to = request.json.reply_to  # type: Comment

        Weixin.msg_sec_check(content)

        if reply_to:
            return reply_to.reply(request.user, content).d()
        return article.comment(request.user, content).d()


class CommentIDView(View):
    @analyse.argument(ArticleParams.aid_getter, CommentParams.cid_getter)
    @Auth.require_login
    def delete(self, request, **kwargs):
        article = request.argument.article
        comment = request.argument.comment
        user = request.user

        comment.assert_belongs_to(article)
        comment.assert_belongs_to(user)

        comment.remove()
        return OK
