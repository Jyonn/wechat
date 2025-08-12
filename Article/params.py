from smartdjango import Params, Validator

from Article.models import Article, Comment


class ArticleParams(metaclass=Params):
    model_class = Article

    aid: Validator
    origin: Validator
    title: Validator
    author: Validator
    self_product: Validator
    require_review: Validator
    allow_open_reply: Validator

    aid_getter = Validator('aid', final_name='article').to(Article.get)


class CommentParams(metaclass=Params):
    model_class = Comment

    content: Validator
    reply_to: Validator

    cid_getter = Validator('cid', final_name='comment').to(Comment.get)
    reply_to_getter = Validator('reply_to', final_name='reply_to').to(Comment.get)
