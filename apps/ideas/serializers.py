from rest_framework import serializers

from .models import Idea


class IdeaValidator(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ("user_id", "content")


class IdeaDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    agree_count = serializers.SerializerMethodField()
    nickname = serializers.CharField()
    avatar = serializers.CharField()

    class Meta:
        model = Idea
        fields = ("user_id", "content", "create_at", "pk", "agree_count", "nickname", "avatar")

    def get_agree_count(self, obj):
        return obj.agree.count()
