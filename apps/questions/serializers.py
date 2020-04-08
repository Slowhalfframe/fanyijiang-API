from rest_framework import serializers

from apps import xss_safe
from apps.userpage.serializers import BasicUserSerializer
from apps.labels.serializers import BasicLabelSerializer
from .models import Question, Answer


class QuestionChecker(serializers.ModelSerializer):
    """用于新建或修改问题时检查数据"""

    class Meta:
        model = Question
        fields = ("title", "content", "is_anonymous",)
        extra_kwargs = {
            "title": {
                "required": True,
            },
            "is_anonymous": {
                "required": True
            },
        }

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

    author = serializers.SerializerMethodField()
    labels = BasicLabelSerializer(many=True)
    type = serializers.CharField(source="kind")
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Question
        fields = ("id", "type", "title", "content", "is_anonymous", "author", "labels", "create_at", "update_at",)

    def get_author(self, obj):
        if obj.is_anonymous:
            return {}
        formatter = BasicUserSerializer(instance=obj.author)
        return formatter.data


class StatQuestionSerializer(BasicQuestionSerializer):
    """用于问题的序列化，增加了与登录用户无关的统计信息"""

    answer_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    follower_count = serializers.IntegerField(source="followers.count")
    read_nums = serializers.SerializerMethodField()  # TODO 阅读次数

    class Meta:
        model = Question
        fields = BasicQuestionSerializer.Meta.fields + (
            "answer_count", "comment_count", "follower_count", "read_nums",)

    def get_answer_count(self, obj):
        return obj.answer_set.filter(is_draft=False, is_deleted=False).count()

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_read_nums(self, obj):
        return 3434  # TODO 返回真实数据


class MeQuestionSerializer(StatQuestionSerializer):
    """用于问题的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_followed = serializers.SerializerMethodField()
    is_answered = serializers.SerializerMethodField()

    # TODO 是否增加is_me，表示登录者即作者？需要重写author属性

    class Meta:
        model = Question
        fields = StatQuestionSerializer.Meta.fields + ("is_followed", "is_answered",)

    def get_is_followed(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.followers.filter(pk=me.pk).exists()

    def get_is_answered(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.answer_set.filter(author=me, is_draft=False, is_deleted=False).exists()


class AnswerChecker(serializers.ModelSerializer):
    """用于新建或修改回答时检查数据"""

    class Meta:
        model = Answer
        fields = ("content", "is_draft", "is_anonymous",)
        extra_kwargs = {
            "content": {
                "required": True,
            },
            "is_draft": {
                "required": True,
            },
            "is_anonymous": {
                "required": True
            },
        }

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("回答没有内容")
        return value


class BasicAnswerSerializer(serializers.ModelSerializer):
    """用于回答的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    question = BasicQuestionSerializer()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ("id", "type", "content", "is_draft", "question", "is_anonymous", "author", "create_at", "update_at",)

    def get_author(self, obj):
        if obj.is_anonymous:
            return {}
        formatter = BasicUserSerializer(instance=obj.author)
        return formatter.data


class StatAnswerSerializer(BasicAnswerSerializer):
    """用于回答的序列化，增加了与登录用户无关的统计信息"""

    comment_count = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = BasicAnswerSerializer.Meta.fields + ("comment_count", "vote_count",)

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_vote_count(self, obj):
        return obj.votes.filter(value=True).count()


class MeAnswerSerializer(StatAnswerSerializer):
    """用于回答的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_voted = serializers.SerializerMethodField()  # 未投票，或票值
    is_commented = serializers.SerializerMethodField()

    # TODO 是否增加is_me，表示登录者即作者？需要重写author属性

    class Meta:
        model = Answer
        fields = StatAnswerSerializer.Meta.fields + ("is_voted", "is_commented",)

    def get_is_voted(self, obj):
        me = self.context.get("me")
        if me is None:
            return None
        my_vote = obj.votes.filter(author=me).first()
        if my_vote is None:
            return None
        return my_vote.value

    def get_is_commented(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.comments.filter(author=me, is_deleted=False).exists()


class MeAnswerWithoutQuestionSerializer(MeAnswerSerializer):
    """用于特殊情况下回答的序列化，与MeAnswerSerializer相比，去掉了问题的信息"""

    class Meta:
        model = Answer
        fields = tuple(i for i in MeAnswerSerializer.Meta.fields if i != "question")
