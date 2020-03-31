from apps.articles_v2.models import Article
from apps.comments.models import Comment
from apps.comments.serializers import CommentChecker, MeCommentSerializer
from apps.questions_v2.models import Question, Answer
from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in

MAPPINGS = {
    "question": Question,
    "answer": Answer,
    "comment": Comment,
    "article": Article,
    # TODO 文章和想法等其他可评论对象
}


class CommentView(CustomAPIView):
    @logged_in
    def post(self, request, kind, id):
        """发表评论"""

        me = request.me
        # TODO 检查用户权限，另外能否自我评论？
        model = MAPPINGS.get(kind)
        if model is None:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        instance = model.objects.filter(pk=id, is_deleted=False).first()
        if instance is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # 某些模型有草稿与正式版之分，需要进一步检测
        if hasattr(model, "is_draft") and instance.is_draft:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        data = {
            "content": request.data.get("content") or "",
        }
        checker = CommentChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            comment = instance.comments.create(author=me, **checker.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeCommentSerializer(instance=comment, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, kind, id):
        """展示评论，可分页"""

        me = self.get_user_profile(request)
        model = MAPPINGS.get(kind)
        if model is None:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        instance = model.objects.filter(pk=id, is_deleted=False).first()
        if instance is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if hasattr(model, "is_draft") and instance.is_draft:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        qs = instance.comments.filter(is_deleted=False)
        data = self.paginate_data(request, qs, MeCommentSerializer, {"me": me})
        return self.success(data)


class OneCommentView(CustomAPIView):
    @logged_in
    def delete(self, request, comment_id):
        """删除评论"""

        me = request.me
        comment = Comment.objects.filter(pk=comment_id, is_deleted=False).first()
        if comment is None:
            return self.success()
        # TODO 哪些评论可以删除？除了作者，还有谁可以删除？真实删除还是逻辑删除？
        return self.success()

    @logged_in
    def put(self, request, comment_id):
        """修改本人的评论"""

        me = request.me
        comment = Comment.objects.filter(pk=comment_id, is_deleted=False).first()
        if comment is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if comment.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        data = {
            "content": request.data.get("content") or "",
        }
        checker = CommentChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            comment.content = checker.validated_data["content"]
            comment.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeCommentSerializer(instance=comment, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, comment_id):
        """查看单个评论"""

        me = self.get_user_profile(request)
        comment = Comment.objects.filter(pk=comment_id, is_deleted=False).first()
        if comment is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        formatter = MeCommentSerializer(instance=comment, context={"me": me})
        return self.success(formatter.data)
