from drf_haystack.serializers import HaystackSerializer

from .search_indexes import QuestionIndex, AnswerIndex, ArticleIndex, IdeaIndex


#
# class QuestionIndexSerializer(HaystackSerializer):
#     class Meta:
#         index_classes = [QuestionIndex]
#         fields = ("text", "id", "title", "content", "kind")
#
#
# class AnswerIndexSerializer(HaystackSerializer):
#     class Meta:
#         index_classes = [AnswerIndex]
#         fields = ("id", "text", "content", "kind")


class UniformIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [AnswerIndex, QuestionIndex, ArticleIndex, IdeaIndex]
        fields = ("id", "kind", "text",)
