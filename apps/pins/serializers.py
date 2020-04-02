import json

from django.conf import settings
from rest_framework import serializers

from apps import legal_image_path
from apps.comments.serializers import BasicUserSerializer
from .models import Idea


class IdeaChecker(serializers.ModelSerializer):
    """用于新建或修改想法时检查数据"""

    class Meta:
        model = Idea
        fields = ("content", "avatars",)
        extra_kwargs = {
            "content": {
                "required": True
            },
            "avatars": {
                "required": True
            }
        }

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            return None
        return value

    def validate_avatars(self, value):
        if not value:
            return "[]"  # json.dumps([])
        try:
            image_paths = json.loads(value)
        except json.JSONDecodeError:
            image_paths = value.split(",")  # 可能是逗号分隔的多个路径
        if not isinstance(image_paths, (list, str)):
            raise serializers.ValidationError("无效的json数据")
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        if len(image_paths) > 9:
            raise serializers.ValidationError("想法最多有9张配图")
        if not all(map(legal_image_path, image_paths)):
            raise serializers.ValidationError("无效的图片路径或格式")
        return json.dumps(image_paths)  # 确保解码后是列表


class BasicIdeaSerializer(serializers.ModelSerializer):
    """用于想法的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")
    author = BasicUserSerializer()
    avatars = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Idea
        fields = ("id", "type", "content", "avatars", "author", "create_at", "update_at",)

    def get_avatars(self, obj):
        image_paths = []
        for i in json.loads(obj.avatars):
            if i.startswith("http"):  # 完整路径
                image_paths.append(i)
            else:  # 不完整路径，进行补全
                image_paths.append(settings.PICTURE_HOST + i)
        return image_paths


class StatIdeaSerializer(BasicIdeaSerializer):
    """用于想法的序列化，增加了与登录用户无关的统计信息"""

    comment_count = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = BasicIdeaSerializer.Meta.fields + ("comment_count", "vote_count",)

    def get_vote_count(self, obj):
        return obj.votes.filter(value=True).count()

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()


class MeIdeaSerializer(StatIdeaSerializer):
    """用于想法的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_commented = serializers.SerializerMethodField()
    is_voted = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = StatIdeaSerializer.Meta.fields + ("is_commented", "is_voted",)

    def get_is_commented(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.comments.filter(author=me, is_deleted=False).exists()

    def get_is_voted(self, obj):
        """与一般的投票不同，想法的投票没有反对票"""
        me = self.context.get("me")
        if me is None:
            return None
        return obj.votes.filter(author=me).exists() or None
