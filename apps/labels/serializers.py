from rest_framework import serializers

from .models import Label


class LabelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ("name", "intro", "pk")
        extra_kwargs = {
            "pk": {
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
