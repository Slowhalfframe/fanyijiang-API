from types import MethodType

from drf_haystack.generics import HaystackGenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from apps.questions.models import Question, Answer
from apps.questions.serializers import NewQuestionSerializer, AnswerCreateSerializer
from apps.search.serializers import UniformIndexSerializer
from apps.utils.api import CustomAPIView


# class QuestionSearchViewSet(HaystackViewSet):
#     index_models = [Question]
#     serializer_class = QuestionIndexSerializer
#
class RootView(ViewSetMixin, HaystackGenericAPIView, CustomAPIView):
    index_models = [Question, Answer]
    serializer_class = UniformIndexSerializer

    def list(self, request):
        # TODO 从request.GET获取搜索关键字并记录
        me = self.get_user_profile(request)
        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_data(request, queryset, self.get_serializer_class())

        temp = {}
        for i in data["results"]:
            kind = i["kind"]
            id = i["id"]
            if kind not in temp:
                temp[kind] = [id]
            else:
                temp[kind].append(id)
        answers = Answer.objects.filter(id__in=temp.get("answer", []))
        questions = Question.objects.filter(id__in=temp.get("question", []))

        data1 = self.paginate_data(request, questions, NewQuestionSerializer, serializer_context={"me": me})
        data2 = self.paginate_data(request, answers, AnswerCreateSerializer, serializer_context={"me": me})
        data = {
            "questions": data1,
            "answers": data2,
            "total": len(queryset),
        }
        return Response(data)
