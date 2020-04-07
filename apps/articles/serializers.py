from rest_framework import serializers

from apps import xss_safe, legal_image_path
from apps.labels.serializers import BasicLabelSerializer
from apps.userpage.serializers import BasicUserSerializer
from .models import Article


class ArticleChecker(serializers.ModelSerializer):
    """用于新建或修改文章时检查数据"""

    class Meta:
        model = Article
        fields = ("title", "content", "cover", "is_draft",)
        extra_kwargs = {
            "title": {
                "required": True,
            },
            "content": {
                "required": True,
            },
            "cover": {
                "required": False,
            },
            "is_draft": {
                "required": True,
            },
        }

    def validate_title(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("文章标题不能为空")
        if not xss_safe(value):
            raise serializers.ValidationError("文章标题含有特殊字符")
        return value

    def validate_content(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("文章主体不能为空")
        return value

    def validate_cover(self, value):
        if not value or value.capitalize() == str(None):
            return None
        if not legal_image_path(value):
            raise serializers.ValidationError("图片路径或类型无效")
        return value


class BasicArticleSerializer(serializers.ModelSerializer):
    """用于文章的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")
    author = BasicUserSerializer()
    labels = BasicLabelSerializer(many=True)
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    update_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")

    class Meta:
        model = Article
        fields = (
            "id", "type", "title", "content", "cover", "is_draft", "author", "labels", "create_at", "update_at",
        )


class StatArticleSerializer(BasicArticleSerializer):
    """用于文章的序列化，增加了与登录用户无关的统计信息"""

    comment_count = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    follower_count = serializers.IntegerField(source="followers.count")

    # TODO 阅读数

    class Meta:
        model = Article
        fields = BasicArticleSerializer.Meta.fields + ("comment_count", "vote_count", "follower_count",)

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_vote_count(self, obj):
        return obj.votes.filter(value=True).count()


class MeArticleSerializer(StatArticleSerializer):
    """用于文章的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_voted = serializers.SerializerMethodField()  # 未投票，或票值
    is_commented = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    # TODO 是否增加is_me，表示登录者即作者？需要重写author属性
    class Meta:
        model = Article
        fields = StatArticleSerializer.Meta.fields + ("is_voted", "is_commented", "is_followed",)

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

    def get_is_followed(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.followers.filter(pk=me.pk).exists()
