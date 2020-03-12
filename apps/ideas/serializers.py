from rest_framework import serializers

from .models import Idea, IdeaComment
from apps.userpage.models import UserProfile


class IdeaValidator(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ("user_id", "content")


class IdeaDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    agree_count = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ("user_id", "content", "create_at", "id", "agree_count", "nickname", "avatar")

    def get_agree_count(self, obj):
        return obj.agree.count()

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname

    def get_avatar(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.avatar


class IdeaCommentValidator(serializers.ModelSerializer):
    class Meta:
        model = IdeaComment
        fields = ("user_id", "think", "content")


class IdeaCommentSerializer(serializers.ModelSerializer):
    agree_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = IdeaComment
        fields = ("user_id", "nickname", "think", "content", "create_at", "agree_count", "id")

    def get_agree_count(self, obj):
        return obj.agree.count()

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname
