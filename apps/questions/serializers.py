from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment
from .search_indexes import QuestionIndex
from apps.labels.models import Label
from apps.userpage.models import UserProfile


class QuestionCreateSerializer(serializers.ModelSerializer):
    """用于提问时的反序列化验证和写入数据库"""
    labels = serializers.ListField(required=True)

    class Meta:
        model = Question
        fields = ("title", "content", "user_id", "labels")

    def validate_labels(self, value):
        value = Label.objects.filter(name__in=value)
        if not value:
            raise serializers.ValidationError("问题的标签不存在")
        return value


class NewQuestionSerializer(serializers.ModelSerializer):
    """用于提问成功后的序列化"""
    nickname = serializers.SerializerMethodField()
    labels = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ("title", "content", "nickname", "labels", "id")

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname


class FollowedQuestionSerializer(serializers.ModelSerializer):
    """本人关注的问题的序列化"""

    class Meta:
        model = Question
        fields = ("title", "content", "id")


class AnswerCreateSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = ("question", "content", "user_id", "id", "nickname")
        read_only_fields = ("id",)

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname


class QuestionFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionFollow
        fields = ("question", "user_id")


class InviteCreateSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)

    class Meta:
        model = QuestionInvite
        fields = ("question", "create_at", "inviting", "invited", "status", "id")
        read_only_fields = ("create_at", "status", "id")

    def validate(self, attrs):
        if attrs["inviting"] == attrs["invited"]:
            raise serializers.ValidationError("不能邀请自己")
        try:
            Answer.objects.get(question=attrs["question"], user_id=attrs["invited"])
        except Answer.DoesNotExist:
            pass
        except Exception as e:
            raise serializers.ValidationError(e.args)
        else:
            raise serializers.ValidationError("不能邀请已回答用户")
        return attrs


class QACommentCreateSerializer(serializers.ModelSerializer):
    qa_id = serializers.PrimaryKeyRelatedField(source="content_object", read_only=True)
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    nickname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QAComment
        fields = ("user_id", "nickname", "content", "create_at", "reply_to_user", "qa_id", "id")
        read_only_fields = ("id", "nickname")

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname


class QACommentDetailSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = QAComment
        fields = ("id", "user_id", "nickname", "content", "create_at", "reply_to_user", "vote_count")

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname


class AnswerInLabelDiscussSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    nickname = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    collected = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "id", "content", "create_at", "nickname", "slug", "avatar", "vote_count", "comment_count", "collected"
        )

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname

    def get_slug(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.slug

    def get_avatar(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.avatar

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_comment_count(self, obj):
        return obj.comment.count()

    def get_collected(self, obj):
        me = self.context["me"]
        if not me:
            return False
        return obj.collect.filter(favorite__user_id=me).exists()  # TODO 这个查询正确吗？


class QuestionInLabelDiscussSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    top_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "title", "content", "top_answer")

    def get_top_answer(self, obj: Question):
        answer = obj.answer_set.first()  # TODO 返回哪个回答
        me = self.context["me"]
        s = AnswerInLabelDiscussSerializer(instance=answer, context={"me": me})
        return s.data


class QuestionIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [QuestionIndex]
        fields = ("text", "id", "title", "content")
