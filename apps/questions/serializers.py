from rest_framework import serializers

from .models import Question, Answer, QuestionFollow
from apps.labels.models import Label


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
    who_asks = serializers.CharField()
    labels = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ("title", "content", "who_asks", "labels", "pk")


class FollowedQuestionSerializer(serializers.ModelSerializer):
    """本人关注的问题的序列化"""

    class Meta:
        model = Question
        fields = ("title", "content", "pk")


class AnswerCreateSerializer(serializers.ModelSerializer):
    who_answers = serializers.CharField(read_only=True)

    class Meta:
        model = Answer
        fields = ("question", "content", "user_id", "pk", "who_answers")
        read_only_fields = ("pk",)


class QuestionFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionFollow
        fields = ("question", "user_id")
