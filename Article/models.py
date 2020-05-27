from SmartDjango import models, E
from django.utils.crypto import get_random_string
from smartify import P


@E.register(id_processor=E.idp_cls_prefix())
class ArticleError:
    NOT_FOUND = E("找不到文章")
    CREATE = E("添加文章失败")
    CREATE_COMMENT = E("留言失败")
    NOT_FOUND_COMMENT = E("找不到留言")


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
    def create(cls, user, author, origin, title):
        try:
            return cls.objects.create(
                user=user,
                title=title,
                author=author,
                origin=origin,
                aid=cls.get_unique_id(),
            )
        except Exception as err:
            raise ArticleError.CREATE(debug_message=err)

    def update(self, origin, title):
        self.origin = origin
        self.title = title
        self.save()

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_comments(self):
        return self.comment_set.filter(reply_to=None).dict(Comment.d_replies)

    def d_base(self):
        return self.dictify('aid', 'title', 'origin', 'author', 'create_time')

    def d(self):
        return self.dictify('aid', 'title', 'origin', 'author', 'create_time', 'comments')

    def d_create(self):
        return self.dictify('aid')

    def comment(self, user, content):
        return Comment.create(self, user, content)


class ArticleP:
    aid, origin, title, author = Article.P('aid', 'origin', 'title', 'author')
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

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_user(self):
        return self.user.d()

    def d(self):
        return self.dictify('content', 'create_time', 'user', 'pk->cid')

    def d_replies(self):
        d = dict(replies=self.comment_set.all().dict(Comment.d))
        d.update(self.d())
        return d


class CommentP:
    content, reply_to = Comment.P('content', 'reply_to')
    reply_to_getter = reply_to.process(Comment.get)
