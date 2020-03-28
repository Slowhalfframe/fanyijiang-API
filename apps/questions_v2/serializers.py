from rest_framework import serializers

from apps import xss_safe
from apps.labels_v2.serializers import BasicLabelSerializer
from apps.userpage.models import UserProfile
from .models import Question, Answer


class SimpleUserSerializer(serializers.ModelSerializer):
    """用于用户的序列化"""

    id = serializers.CharField(source="uid")
    type = serializers.CharField(source="kind")
    homepage = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "type", "slug", "nickname", "gender", "avatar", "autograph", "homepage",)

    def get_homepage(self, obj):
        return ""  # TODO 用户主页的地址


class QuestionChecker(serializers.ModelSerializer):
    """用于新建或修改问题时检查数据"""

    class Meta:
        model = Question
        fields = ("title", "content",)

    def validate_title(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("问题标题不能为空")
        if not xss_safe(value):
            raise serializers.ValidationError("问题标题含有特殊字符")
        return value

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            return None
        return value


class BasicQuestionSerializer(serializers.ModelSerializer):
    """用于问题的序列化，返回最基础的信息"""

    author = SimpleUserSerializer()
    labels = BasicLabelSerializer(many=True)
    type = serializers.CharField(source="kind")
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Question
        fields = ("id", "type", "title", "content", "author", "labels", "create_at", "update_at",)


class StatQuestionSerializer(BasicQuestionSerializer):
    """用于问题的序列化，增加了与登录用户无关的统计信息"""

    answer_count = serializers.SerializerMethodField()  # TODO 回答数
    comment_count = serializers.SerializerMethodField()  # TODO 评论数
    follower_count = serializers.SerializerMethodField()  # TODO 关注者个数
    view_count = serializers.SerializerMethodField()  # TODO 阅读次数

    class Meta:
        model = Question
        fields = BasicQuestionSerializer.Meta.fields + (
            "answer_count", "comment_count", "follower_count", "view_count",)

    def get_answer_count(self, obj):
        return obj.answer_set.filter(is_draft=False, is_deleted=False).count()

    def get_comment_count(self, obj):
        return 10  # TODO 返回真实数据

    def get_follower_count(self, obj):
        return 100  # TODO 返回真实数据

    def get_view_count(self, obj):
        return 3434  # TODO 返回真实数据


class MeQuestionSerializer(StatQuestionSerializer):
    """用于问题的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_followed = serializers.SerializerMethodField()  # TODO 是否已关注
    is_answered = serializers.SerializerMethodField()  # TODO 是否已经回答

    class Meta:
        model = Question
        fields = StatQuestionSerializer.Meta.fields + ("is_followed", "is_answered",)

    def get_is_followed(self, obj):
        return False  # TODO 返回真实数据

    def get_is_answered(self, obj):
        return False  # TODO 返回真实数据


class AnswerChecker(serializers.ModelSerializer):
    """用于新建或修改回答时检查数据"""

    class Meta:
        model = Answer
        fields = ("content", "is_draft",)

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("回答没有内容")
        return value

    def validate_is_draft(self, value):
        if value not in (True, False):
            raise serializers.ValidationError("没有指明回答是否是草稿")
        return value


class BasicAnswerSerializer(serializers.ModelSerializer):
    """用于回答的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    question = BasicQuestionSerializer()
    author = SimpleUserSerializer()

    class Meta:
        model = Answer
        fields = ("id", "type", "content", "is_draft", "question", "author", "create_at", "update_at",)


class StatAnswerSerializer(BasicAnswerSerializer):
    """用于回答的序列化，增加了与登录用户无关的统计信息"""

    comment_count = serializers.SerializerMethodField()  # TODO 评论数
    vote_count = serializers.SerializerMethodField()  # TODO 赞成票数

    class Meta:
        model = Answer
        fields = BasicAnswerSerializer.Meta.fields + ("comment_count", "vote_count",)

    def get_comment_count(self, obj):
        return 100  # TODO 返回真实数据

    def get_vote_count(self, obj):
        return 100  # TODO 返回真实数据


class MeAnswerSerializer(StatAnswerSerializer):
    """用于回答的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_voted = serializers.SerializerMethodField()  # TODO 是否已经投票，或票值
    is_commented = serializers.SerializerMethodField()  # TODO 是否已经评论

    class Meta:
        model = Answer
        fields = StatAnswerSerializer.Meta.fields + ("is_voted", "is_commented",)

    def get_is_voted(self, obj):
        return None  # TODO 返回真实数据

    def get_is_commented(self, obj):
        return False  # TODO 返回真实数据
