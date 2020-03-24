from drf_haystack.viewsets import HaystackViewSet

from apps.questions.models import Question
from apps.search.serializers import QuestionIndexSerializer


class QuestionSearchViewSet(HaystackViewSet):
    index_models = [Question]
    serializer_class = QuestionIndexSerializer
