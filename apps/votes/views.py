from apps.articles.models import Article
from apps.comments.models import Comment
from apps.pins.models import Idea
from apps.questions.models import Answer
from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in
from .serializers import VoteChecker

MAPPINGS = {
    "answer": Answer,
    "comment": Comment,
    "article": Article,
    "idea": Idea,
}


class VoteView(CustomAPIView):
    @logged_in
    def post(self, request, kind, id):
        """投票，如果已经投过票则直接修改，每人对每个对象只能投一票"""

        me = request.me
        # TODO 检查用户权限
        model = MAPPINGS.get(kind)
        if model is None:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        instance = model.objects.filter(pk=id, is_deleted=False).first()
        if instance is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if hasattr(model, "is_draft") and instance.is_draft:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # TODO 能给自己投票吗？
        if model == Idea:  # 想法只接受赞成票
            data = {"value": True}
        else:
            data = {"value": request.data.get("value"), }
        checker = VoteChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            instance.votes.update_or_create(author=me, defaults=checker.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def delete(self, request, kind, id):
        """删除本人的投票"""

        me = request.me
        model = MAPPINGS.get(kind)
        if model is None:
            return self.success()
        instance = model.objects.filter(pk=id, is_deleted=False).first()
        if instance is None:
            return self.success()
        qs = instance.votes.filter(author=me)
        if not qs.exists():
            return self.success()
        try:
            qs.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()
