import json

from rest_framework import serializers
from django.conf import settings

from .models import Idea, IdeaComment
from apps.userpage.models import UserProfile


class IdeaValidator(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ("user_id", "content", "avatars")

    def validate_avatars(self, value):
        file_path_list = json.loads(value)
        # TODO 验证图片路径和格式
        return value


class IdeaDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    agree_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    avatars = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ("id", "content", "create_at", "agree_count", "author_info", "avatars", "liked")

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

    def get_avatars(self, obj):
        avatars = json.loads(obj.avatars)
        avatars = [settings.PICTURE_HOST + settings.UPLOAD_PREFIX + "/" + i for i in avatars]
        return avatars

    def get_liked(self, obj):
        me = self.context["me"]
        if not me:
            return False
        return obj.agree.filter(user_id=me.uid).exists()


class IdeaCommentValidator(serializers.ModelSerializer):
    class Meta:
        model = IdeaComment
        fields = ("user_id", "think", "content")


class IdeaCommentSerializer(serializers.ModelSerializer):
    agree_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    author_info = serializers.SerializerMethodField()
    think_id = serializers.IntegerField(source="think.pk")
    liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = IdeaComment
        fields = ("id", "think_id", "content", "create_at", "agree_count", "author_info", "liked", "is_author")

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

    def get_liked(self, obj):
        me = self.context["me"]
        if not me:
            return False
        return obj.agree.filter(user_id=me.uid).exists()

    def get_is_author(self, obj):
        return obj.user_id == obj.think.user_id
