from rest_framework import serializers

from apps import xss_safe
from apps.labels_v2.serializers import BasicLabelSerializer
from apps.questions_v2.models import Question
from apps.userpage.models import UserProfile


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
        return 100  # TODO 返回真实数据

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
