from typing import Union

from diq import Dictify
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string
from smartdjango import Error

from Article.validators import ArticleErrors, ArticleValidator
from User.models import User


class Article(models.Model, Dictify):
    vldt = ArticleValidator

    user = models.ForeignKey(
        'User.MiniUser',
        on_delete=models.CASCADE,
    )

    aid = models.CharField(
        verbose_name='文章ID',
        max_length=vldt.MAX_AID_LENGTH,
        unique=True,
        validators=[vldt.aid],
    )

    origin = models.CharField(
        max_length=vldt.MAX_ORIGIN_LENGTH,
        null=True,
        default=None,
    )

    author = models.CharField(
        max_length=vldt.MAX_AUTHOR_LENGTH,
        null=True,
        default=None,
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    title = models.CharField(
        max_length=vldt.MAX_TITLE_LENGTH,
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
            raise ArticleErrors.NOT_FOUND

    @classmethod
    def get_unique_id(cls):
        while True:
            aid = get_random_string(length=6)
            try:
                cls.get(aid)
            except Error:
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
            raise ArticleErrors.CREATE(details=err)

    def update(self, title, origin, author):
        self.origin = origin
        self.title = title
        self.author = author
        self.save()

    def assert_belongs_to(self, user):
        if self.user != user:
            raise ArticleErrors.NOT_OWNER

    def remove(self):
        self.delete()

    def get_comments(self, show_all=False, selected=True):
        comments = self.comment_set.filter(reply_to=None)
        if not show_all:
            comments = comments.filter(selected=selected)
        return comments.order_by('pk')

    def _dictify_create_time(self):
        return self.create_time.timestamp()

    def _dictify_comments(self):
        comments = self.comment_set.filter(reply_to=None)
        if self.require_review:
            comments = comments.filter(selected=True)
        comments = comments.order_by('pk')
        # .dict(Comment.d_replies, show_all)
        return [comment.d_replies() for comment in comments]

    def _dictify_all_comments(self):
        if not self.require_review:
            return None
        comments = self.comment_set.filter(reply_to=None)
        if self.require_review:
            comments = comments.filter(selected=True)
        comments = comments.order_by('pk')
        return [comment.d_all() for comment in comments]

    def _dictify_my_comments(self, user):
        if not self.require_review:
            return []
        comments = self.comment_set.filter(
            ~Q(selected=True), user=user, reply_to=None).order_by('pk')
        return [comment.d_replies() for comment in comments]

    def _dictify_user(self):
        return self.user.d()

    def d_base(self):
        return self.dictify(
            'aid', 'title', 'origin', 'author', 'create_time', 'self_product',
            'require_review', 'allow_open_reply')

    def d(self, user):
        d = self.d_base()
        if self.user == user:
            d.update(self.dictify('comments', 'user', 'all_comments'))
        else:
            d.update(self.dictify('comments', 'user'))
            d['my_comments'] = self._dictify_my_comments(user)
        return d

    def d_create(self):
        return self.dictify('aid')

    def comment(self, user, content):
        return Comment.create(self, user, content)


class Comment(models.Model, Dictify):
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
        default=None,
        null=True,
        blank=True,
    )

    @classmethod
    def get(cls, cid):
        try:
            return cls.objects.get(pk=cid)
        except cls.DoesNotExist:
            raise ArticleErrors.NOT_FOUND_COMMENT

    @classmethod
    def create(cls, article, user, content):
        try:
            return cls.objects.create(
                article=article,
                user=user,
                content=content,
                reply_to=None,
                selected=False,
            )
        except Exception as err:
            raise ArticleErrors.CREATE_COMMENT(details=err)

    def reply(self, user, content):
        reply_to = self.reply_to or self
        if reply_to and not self.article.allow_open_reply:
            if user not in [self.article.user, reply_to.user]:
                raise ArticleErrors.DENY_OPEN_REPLY

        try:
            return Comment.objects.create(
                article=self.article,
                user=user,
                content=content,
                reply_to=reply_to,
                selected=False,
            )
        except Exception as err:
            raise ArticleErrors.CREATE_COMMENT(details=err)

    def assert_belongs_to(self, owner: Union[Article, User]):
        if isinstance(owner, Article):
            if self.article != owner:
                raise ArticleErrors.NOT_MATCH
        else:
            if owner not in [self.user, self.article.user]:
                raise ArticleErrors.NOT_OWNER

    def remove(self):
        self.delete()

    def _dictify_create_time(self):
        return self.create_time.timestamp()

    def _dictify_user(self):
        return self.user.d()

    def d(self):
        return self.dictify('content', 'create_time', 'user', 'pk->cid')

    def d_replies(self):
        replies = self.comment_set.all()
        if self.article.require_review:
            replies = replies.filter(selected=True)
        # dict_ = dict(replies=replies.dict(Comment.d))
        dict_ = dict(replies=[reply.d() for reply in replies])
        dict_.update(self.d())
        return dict_

    def d_all(self):
        replies = self.comment_set.all()
        # d = dict(replies=replies.dict(Comment.d))
        dict_ = dict(replies=[reply.d() for reply in replies])
        dict_.update(self.d())
        return dict_
