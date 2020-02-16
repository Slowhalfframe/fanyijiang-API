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


class ChildLabelSerializer(serializers.Serializer):
    parent = LabelCreateSerializer()
    children = LabelCreateSerializer(many=True)
