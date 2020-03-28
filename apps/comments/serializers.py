from rest_framework import serializers

from apps.userpage.models import UserProfile
from .models import Comment


class BasicUserSerializer(serializers.ModelSerializer):
    """用于用户的序列化，返回最基础的信息"""

    id = serializers.CharField(source="uid")
    type = serializers.CharField(source="kind")
    homepage = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "type", "slug", "nickname", "gender", "avatar", "autograph", "homepage",)

    def get_homepage(self, obj):
        return ""  # TODO 用户主页的地址


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
    author = serializers.SerializerMethodField()
    respondent = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Comment
        fields = ("id", "type", "content", "author", "respondent", "create_at", "update_at",)

    @staticmethod
    def insert_is_author(obj, user):
        data = BasicUserSerializer(instance=user).data
        # is_author表示此用户是否是该评论的根对象的作者
        data["is_author"] = obj.root_object.author == user
        return data

    def get_author(self, obj):
        user = obj.author
        return self.insert_is_author(obj, user)

    def get_respondent(self, obj):
        user = obj.respondent
        return self.insert_is_author(obj, user)


class StatCommentSerializer(BasicCommentSerializer):
    """用于评论的序列化，增加了与登录用户无关的统计信息和子评论的基本信息"""

    children = BasicCommentSerializer(many=True, source="comments")
    comment_count = serializers.SerializerMethodField()  # 子评论数
    vote_count = serializers.SerializerMethodField()  # TODO 赞成票数

    class Meta:
        model = Comment
        fields = BasicCommentSerializer.Meta.fields + ("children", "vote_count", "comment_count",)

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_vote_count(self, obj):
        return 100  # TODO 返回真实数据


class MeCommentSerializer(StatCommentSerializer):
    """用于评论的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_voted = serializers.SerializerMethodField()  # TODO 是否已经投票，或票值
    is_commented = serializers.SerializerMethodField()  # TODO 是否已经评论
    # 重写author和respondent，增加is_me表示是否是当前登录者
    author = serializers.SerializerMethodField()
    respondent = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = StatCommentSerializer.Meta.fields + ("is_voted", "is_commented",)

    def get_is_voted(self, obj):
        return None  # TODO 返回真实数据

    def get_is_commented(self, obj):
        return False  # TODO 返回真实数据

    def insert_is_me(self, obj, user):
        data = self.insert_is_author(obj, user)
        me = self.context.get("me")
        if me is None:
            data["is_me"] = False
        else:
            data["is_me"] = user == me
        return data

    def get_author(self, obj):
        user = obj.author
        return self.insert_is_me(obj, user)

    def get_respondent(self, obj):
        user = obj.respondent
        return self.insert_is_me(obj, user)
