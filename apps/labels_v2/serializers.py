import html

from rest_framework import serializers

from apps import xss_safe, legal_image_path
from .models import Label, LabelFollow


class LabelChecker(serializers.ModelSerializer):
    """用于新建或修改标签时检查数据"""

    class Meta:
        model = Label
        fields = ("name", "intro", "avatar",)

    def validate_name(self, value):
        if not xss_safe(value):
            raise serializers.ValidationError("标签名称含有特殊字符")
        return value

    def validate_intro(self, value):
        if not value:
            return None
        return html.escape(value)

    def validate_avatar(self, value):
        if not value:
            return None
        if not legal_image_path(value):
            return serializers.ValidationError("图片路径或类型无效")
        return value


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ("id", "name", "intro", "avatar",)
