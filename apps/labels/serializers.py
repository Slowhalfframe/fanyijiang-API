from rest_framework import serializers

from .models import Label


class LabelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ("name", "intro", "id")
        extra_kwargs = {
            "id": {
                "read_only": True
            }
        }


class LabelUpdateSerializer(serializers.Serializer):
    old_name = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    intro = serializers.CharField(required=True)

    def validate_old_name(self, value):
        try:
            label = Label.objects.get(name=value)
        except Label.DoesNotExist as e:
            raise serializers.ValidationError(e)
        return label


class ChildLabelSerializer(serializers.Serializer):
    parent = LabelCreateSerializer()
    children = LabelCreateSerializer(many=True)


class LabelDetailSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    question_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    followed = serializers.SerializerMethodField()
    parent = serializers.StringRelatedField(source="label_set", many=True)
    children = serializers.StringRelatedField(many=True)

    class Meta:
        model = Label
        fields = ("id", "name", "intro", "question_count", "follower_count", "followed", "parent", "children",)

    def get_question_count(self, obj):
        return obj.question_set.count()

    def get_follower_count(self, obj):
        return obj.labelfollow_set.count()

    def get_followed(self, obj: Label):
        me = self.context["me"]  # None或UserProfile对象
        if not me:  # 无人登录时，看作未关注
            return False
        return obj.labelfollow_set.filter(user_id=me.uid).exists()  # 登录时，返回用户的关注状态
