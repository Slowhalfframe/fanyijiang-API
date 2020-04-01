from rest_framework import serializers

from apps import xss_safe, legal_image_path
from .models import Label


class LabelChecker(serializers.ModelSerializer):
    """用于新建或修改标签时检查数据"""

    class Meta:
        model = Label
        fields = ("name", "intro", "avatar",)
        extra_kwargs = {
            "name": {
                "required": True,
            }
        }

    def validate_name(self, value):
        if not value or value.capitalize() == str(None):
            raise serializers.ValidationError("标签名称不能为空")
        if not xss_safe(value):
            raise serializers.ValidationError("标签名称含有特殊字符")
        return value

    def validate_intro(self, value):
        if not value or value.capitalize() == str(None):
            return None
        return value

    def validate_avatar(self, value):
        if not value or value.capitalize() == str(None):
            return None
        if not legal_image_path(value):
            raise serializers.ValidationError("图片路径或类型无效")
        return value


class BasicLabelSerializer(serializers.ModelSerializer):
    """用于标签的序列化，返回最基础的信息"""

    type = serializers.CharField(source="kind")

    class Meta:
        model = Label
        fields = ("id", "type", "name", "intro", "avatar",)


class StatLabelSerializer(BasicLabelSerializer):
    """用于标签的序列化，增加了与登录用户无关的统计信息"""

    follower_count = serializers.IntegerField(source="followers.count")
    question_count = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = BasicLabelSerializer.Meta.fields + ("follower_count", "question_count", "article_count",)

    def get_question_count(self, obj):
        return obj.question_set.filter(is_deleted=False).count()

    def get_article_count(self, obj):
        return obj.article_set.filter(is_deleted=False, is_draft=False).count()


class MeLabelSerializer(StatLabelSerializer):
    """用于标签的序列化，增加了与登录用户有关的信息，需要传入当前登录用户"""

    is_followed = serializers.SerializerMethodField()  # 是否已经关注

    class Meta:
        model = Label
        fields = StatLabelSerializer.Meta.fields + ("is_followed",)

    def get_is_followed(self, obj):
        me = self.context.get("me")
        if me is None:
            return False
        return obj.followers.filter(pk=me.pk).exists()
