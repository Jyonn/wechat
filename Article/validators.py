from smartdjango import Error, Code


@Error.register
class ArticleErrors:
    NOT_FOUND = Error("找不到文章", code=Code.NotFound)
    CREATE = Error("添加文章失败", code=Code.InternalServerError)
    CREATE_COMMENT = Error("留言失败", code=Code.InternalServerError)
    NOT_FOUND_COMMENT = Error("找不到留言", code=Code.NotFound)
    NOT_OWNER = Error("没有权限", code=Code.Unauthorized)
    NOT_MATCH = Error("评论和文章不匹配", code=Code.BadRequest)
    DENY_OPEN_REPLY = Error("文章没有开启自由评论回复功能", code=Code.Forbidden)
    AID_TOO_SHORT = Error("文章ID过短，至少为{length}位", code=Code.BadRequest)


class ArticleValidator:
    MAX_AID_LENGTH = 6
    MIN_AID_LENGTH = 6
    MAX_ORIGIN_LENGTH = 20
    MAX_AUTHOR_LENGTH = 20
    MAX_TITLE_LENGTH = 50

    @classmethod
    def aid(cls, aid: str):
        if len(aid) < cls.MIN_AID_LENGTH:
            raise ArticleErrors.AID_TOO_SHORT(length=cls.MIN_AID_LENGTH)
        return aid

