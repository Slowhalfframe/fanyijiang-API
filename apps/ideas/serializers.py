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
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ("id", "content", "create_at", "agree_count", "author_info")

    def get_agree_count(self, obj):
        return obj.agree.count()

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "slug": author.slug
        }
        return data


class IdeaCommentValidator(serializers.ModelSerializer):
    class Meta:
        model = IdeaComment
        fields = ("user_id", "think", "content")


class IdeaCommentSerializer(serializers.ModelSerializer):
    agree_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    author_info = serializers.SerializerMethodField()
    think_id = serializers.IntegerField(source="think.pk")

    class Meta:
        model = IdeaComment
        fields = ("id", "think_id", "content", "create_at", "agree_count", "author_info")

    def get_agree_count(self, obj):
        return obj.agree.count()

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "slug": author.slug
        }
        return data
