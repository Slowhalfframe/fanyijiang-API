from rest_framework import serializers
from .models import Vote


class VoteChecker(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("value",)
        extra_kwargs = {
            "value": {
                "required": True
            }
        }
