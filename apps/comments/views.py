from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in


class CommentView(CustomAPIView):
    @logged_in
    def post(self, request, kind, id):
        """发表评论"""

    def get(self, request, kind, id):
        """展示评论，可分页"""
        pass


class OneCommentView(CustomAPIView):
    @logged_in
    def delete(self, request, comment_id):
        """删除评论"""

    @logged_in
    def put(self, request, comment_id):
        """修改评论"""

    def get(self, request, comment_id):
        """查看单个评论"""
