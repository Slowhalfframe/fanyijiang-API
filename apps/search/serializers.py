from drf_haystack.serializers import HaystackSerializer

from .search_indexes import QuestionIndex


class QuestionIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [QuestionIndex]
        fields = ("text", "id", "title", "content")
