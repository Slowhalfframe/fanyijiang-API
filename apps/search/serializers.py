from drf_haystack.serializers import HaystackSerializer

from .search_indexes import QuestionIndex, AnswerIndex, ArticleIndex, IdeaIndex, UserIndex


class UniformIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [AnswerIndex, QuestionIndex, ArticleIndex, IdeaIndex]
        fields = ("id", "kind", "text",)


class UserIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [UserIndex, ]
        fields = ("text",)
