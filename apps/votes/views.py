from apps.comments.models import Comment
from apps.questions_v2.models import Answer
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in

MAPPINGS = {
    "answer": Answer,
    "comment": Comment,
    # TODO 文章和想法等其他可投票对象
}


class VoteView(CustomAPIView):
    @logged_in
    def post(self, request, kind, id):
        """投票，如果已经投过票则直接修改，每人对每个对象只能投一票"""

    @logged_in
    def delete(self, request, kind, id):
        """删除本人的投票"""
