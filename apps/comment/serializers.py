from rest_framework import serializers

from apps.questions_v2.serializers import SimpleUserSerializer
from .models import Comment


class CommentChecker(serializers.ModelSerializer):
    """用于新建或修改评论时检查数据"""

    class Meta:
        model = Comment
        fields = ("content",)

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            return None
        return value


class BasicCommentSerializer(serializers.ModelSerializer):
    """用于评论的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")
    author = SimpleUserSerializer()
    respondent = SimpleUserSerializer()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Comment
        fields = ("id", "type", "content", "author", "respondent", "create_at", "update_at",)


class StatCommentSerializer(BasicCommentSerializer):
    """用于评论的序列化，增加了与登录用户无关的统计信息和子评论的基本信息"""

    children = BasicCommentSerializer(many=True)
    comment_count = serializers.SerializerMethodField()  # TODO 子评论数
    vote_count = serializers.SerializerMethodField()  # TODO 赞成票数

    class Meta:
        model = Comment
        fields = BasicCommentSerializer.Meta.fields + ("children", "vote_count", "comment_count",)

    def get_comment_count(self, obj):
        return 100  # TODO 返回真实数据

    def get_vote_count(self, obj):
        return 100  # TODO 返回真实数据


class MeCommentSerializer(StatCommentSerializer):
    """用于评论的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_voted = serializers.SerializerMethodField()  # TODO 是否已经投票，或票值
    is_commented = serializers.SerializerMethodField()  # TODO 是否已经评论

    class Meta:
        model = Comment
        fields = StatCommentSerializer.Meta.fields + ("is_voted", "is_commented",)

    def get_is_voted(self, obj):
        return None  # TODO 返回真实数据

    def get_is_commented(self, obj):
        return False  # TODO 返回真实数据
