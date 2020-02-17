from rest_framework import serializers

from .models import Question


class QuestionCreateSerializer(serializers.ModelSerializer):
    who_asks = serializers.CharField(read_only=True)

    class Meta:
        model = Question
        fields = ("title", "content", "labels", "who_asks", "user_id", "pk")
        extra_kwargs = {
            "pk": {
                "read_only": True
            },
            "user_id": {
                "read_only": True
            }
        }
