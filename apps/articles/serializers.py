import os
import html

from rest_framework import serializers

from .models import Article, ArticleComment
from apps.labels.models import Label
from apps.labels.serializers import SimpleLabelSerializer
from apps.userpage.models import UserProfile


class ArticleCreateSerializer(serializers.ModelSerializer):
    """只用于反序列化验证和保存"""
    labels = serializers.ListField(required=True)

    class Meta:
        model = Article
        fields = ("user_id", "title", "content", "image", "status", "labels",)

    def validate(self, attrs):
        status = attrs["status"]
        label_names = attrs.pop("labels")
        labels = Label.objects.filter(name__in=label_names)
        attrs["labels"] = labels
        if status not in ("draft", "published"):
            raise serializers.ValidationError("状态只有两种")
        if status == "published" and not labels:
            raise serializers.ValidationError("只有草稿可以没有标签")
        return attrs

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
        # value = html.escape(value)
        return value


class NewArticleSerializer(serializers.ModelSerializer):
    """只用于序列化输出"""
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    labels = SimpleLabelSerializer(many=True)
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id", "author_info", "title", "content", "image", "status", "create_at", "update_at", "labels",
        )

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "slug": author.slug,
            "autograph": author.autograph,
        }
        return data


class ArticleDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    labels = SimpleLabelSerializer(many=True)
    vote_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id", "author_info", "title", "content", "image", "status", "create_at", "update_at",
            "labels", "vote_count", "comment_count", "voted",
        )

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        me = self.context["me"]
        if not me:
            followed = False
        else:
            followed = author.as_idol.filter(fans__uid=me.uid).exists()
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "slug": author.slug,
            "autograph": author.autograph,
            "followed": followed
        }
        return data

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_comment_count(self, obj):
        return obj.articlecomment_set.count()

    def get_voted(self, obj):
        me = self.context["me"]
        if not me:
            return None
        my_vote = obj.vote.filter(user_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value


class ArticleCommentSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    vote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField(read_only=True)
    is_author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ArticleComment
        fields = ("id", "article", "user_id", "author_info", "receiver_info", "content", "reply_to_user", "create_at",
                  "vote_count", "voted", "is_author")
        read_only_fields = ("id", "create_at", "vote_count", "author_info", "receiver_info", "voted", "is_author")
        extra_kwargs = {
            "user_id": {
                "write_only": True
            },
            "reply_to_user": {
                "write_only": True
            }
        }

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "slug": author.slug,
        }
        return data

    def get_receiver_info(self, obj):
        receiver = UserProfile.objects.get(uid=obj.reply_to_user)
        data = {
            "nickname": receiver.nickname,
            "avatar": receiver.avatar,
            "slug": receiver.slug,
        }
        return data

    def validate_article(self, value):
        if value.status != "published":
            raise serializers.ValidationError("不能评论草稿")
        return value

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_voted(self, obj: ArticleComment):
        me = self.context["me"]
        if not me:
            return None
        my_vote = obj.vote.filter(user_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_is_author(self, obj):
        return obj.user_id == obj.article.user_id
