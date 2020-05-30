from typing import Union

from SmartDjango import models, E
from django.utils.crypto import get_random_string
from smartify import P

from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class ArticleError:
    NOT_FOUND = E("找不到文章")
    CREATE = E("添加文章失败")
    CREATE_COMMENT = E("留言失败")
    NOT_FOUND_COMMENT = E("找不到留言")
    NOT_OWNER = E("没有权限")
    NOT_MATCH = E("评论和文章不匹配")


class Article(models.Model):
    user = models.ForeignKey(
        'User.MiniUser',
        on_delete=models.CASCADE,
    )

    aid = models.CharField(
        verbose_name='文章ID',
        max_length=6,
        min_length=6,
        unique=True,
    )

    origin = models.CharField(
        max_length=20,
        null=True,
        default=None,
    )

    author = models.CharField(
        max_length=20,
        null=True,
        default=None,
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    title = models.CharField(
        max_length=50,
    )

    self_product = models.BooleanField(
        verbose_name='原创声明',
        default=False,
        null=True,
    )

    require_review = models.BooleanField(
        verbose_name='需要审核',
        default=False,
        null=True,
    )

    allow_open_reply = models.BooleanField(
        verbose_name='允许公开回复',
        default=False,
        null=True,
    )

    @classmethod
    def get(cls, aid):
        try:
            return cls.objects.get(aid=aid)
        except cls.DoesNotExist:
            raise ArticleError.NOT_FOUND

    @classmethod
    def get_unique_id(cls):
        while True:
            aid = get_random_string(length=6)
            try:
                cls.get(aid)
            except E:
                return aid

    @classmethod
    def create(cls, user, author, origin, title, self_product, require_review, allow_open_reply):
        try:
            return cls.objects.create(
                user=user,
                title=title,
                author=author,
                origin=origin,
                self_product=self_product,
                require_review=require_review,
                allow_open_reply=allow_open_reply,
                aid=cls.get_unique_id(),
            )
        except Exception as err:
            raise ArticleError.CREATE(debug_message=err)

    def update(self, title, origin, author):
        self.origin = origin
        self.title = title
        self.author = author
        self.save()

    def assert_belongs_to(self, user):
        if self.user != user:
            raise ArticleError.NOT_OWNER

    def remove(self):
        self.delete()

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_comments(self, show_all=False):
        if not self.require_review and show_all:
            return
        comments = self.comment_set.filter(reply_to=None)
        if self.require_review:
            comments = comments.filter(selected=True)
        return comments.order_by('pk').dict(Comment.d_replies, show_all)

    def _readable_my_comments(self, user):
        return self.comment_set.filter(
            user=user, reply_to=None).order_by('pk').dict(Comment.d_replies)

    def _readable_user(self):
        return self.user.d()

    def d_base(self):
        return self.dictify(
            'aid', 'title', 'origin', 'author', 'create_time', 'self_product',
            'require_review', 'allow_open_reply')

    def d(self, user):
        d = self.d_base()
        if self.user == user:
            d.update(self.dictify('comments', 'user', ('comments->all_comments', True)))
        else:
            d.update(self.dictify('comments', 'user', ('my_comments', user)))
        return d

    def d_create(self):
        return self.dictify('aid')

    def comment(self, user, content):
        return Comment.create(self, user, content)


class ArticleP:
    aid, origin, title, author, self_product, require_review, allow_open_reply = Article.P(
        'aid', 'origin', 'title', 'author', 'self_product', 'require_review', 'allow_open_reply')
    aid_getter = aid.rename('aid', yield_name='article', stay_origin=True).process(Article.get)


class Comment(models.Model):
    article = models.ForeignKey(
        'Article.Article',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        'User.MiniUser',
        on_delete=models.CASCADE,
    )

    content = models.TextField()

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )

    selected = models.BooleanField(
        verbose_name='精选评论',
        default=False,
    )

    @classmethod
    def get(cls, cid):
        try:
            return cls.objects.get(pk=cid)
        except cls.DoesNotExist:
            raise ArticleError.NOT_FOUND_COMMENT

    @classmethod
    def create(cls, article, user, content):
        try:
            return cls.objects.create(
                article=article,
                user=user,
                content=content,
                reply_to=None,
            )
        except Exception as err:
            raise ArticleError.CREATE_COMMENT(debug_message=err)

    def reply(self, user, content):
        reply_to = self.reply_to or self
        try:
            return Comment.objects.create(
                article=self.article,
                user=user,
                content=content,
                reply_to=reply_to,
            )
        except Exception as err:
            raise ArticleError.CREATE_COMMENT(debug_message=err)

    def assert_belongs_to(self, owner: Union[Article, User]):
        if isinstance(owner, Article):
            if self.article != owner:
                raise ArticleError.NOT_MATCH
        else:
            if owner not in [self.user, self.article.user]:
                raise ArticleError.NOT_OWNER

    def remove(self):
        self.delete()

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_user(self):
        return self.user.d()

    def d(self):
        return self.dictify('content', 'create_time', 'user', 'pk->cid')

    def d_replies(self, show_all=False):
        replies = self.comment_set.all()
        if self.article.require_review and not show_all:
            replies = replies.filter(selected=True)
        d = dict(replies=replies.dict(Comment.d))
        d.update(self.d())
        return d


class CommentP:
    content, reply_to = Comment.P('content', 'reply_to')
    cid_getter = P('cid', yield_name='comment').process(int).process(Comment.get)
    reply_to_getter = reply_to.process(Comment.get)
