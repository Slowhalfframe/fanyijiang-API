import os
import html

from rest_framework import serializers

from .models import Article, ArticleComment
from apps.labels.models import Label


class ArticleCreateSerializer(serializers.ModelSerializer):
    """只用于反序列化验证和保存"""
    labels = serializers.ListField(required=True)

    class Meta:
        model = Article
        fields = ("user_id", "title", "content", "image", "status", "labels",)

    def validate_labels(self, value):
        value = Label.objects.filter(name__in=value)
        if not value:
            raise serializers.ValidationError("标签不存在")
        return value

    def validate_image(self, value):
        # TODO 应该检查以确保文件是存在的，至少是合格的文件路径
        if value == "":  # 允许没有缩略图
            return value
        path, ext = os.path.splitext(value)
        if not ext:
            raise serializers.ValidationError("文件名为空")
        if ext not in (".gif", ".bmp", ".jpg", ".jpeg", ".png"):
            raise serializers.ValidationError("无效的图片类型")
        return value

    def validate_content(self, value):
        value = html.escape(value)
        return value


class NewArticleSerializer(serializers.ModelSerializer):
    """只用于序列化输出"""
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    labels = serializers.StringRelatedField(many=True)

    class Meta:
        model = Article
        fields = ("id", "user_id", "title", "content", "image", "status", "create_at", "update_at", "labels",)


class ArticleDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    labels = serializers.StringRelatedField(many=True)
    vote_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id", "user_id", "title", "content", "image", "status", "create_at", "update_at", "labels", "vote_count",
            "comment_count")

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_comment_count(self, obj):
        return obj.articlecomment_set.count()


class ArticleCommentSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = ArticleComment
        fields = ("article", "user_id", "content", "reply_to_user", "id", "create_at", "vote_count")
        read_only_fields = ("id", "create_at", "reply_to_user", "vote_count")

    def validate_article(self, value):
        if value.status != "published":
            raise serializers.ValidationError("不能评论草稿")
        return value

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()
