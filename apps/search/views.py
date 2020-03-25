from drf_haystack.generics import HaystackGenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from apps.questions.models import Question, Answer
from apps.questions.serializers import NewQuestionSerializer, AnswerCreateSerializer
from apps.articles.models import Article
from apps.articles.serializers import ArticleDetailSerializer
from apps.ideas.models import Idea
from apps.ideas.serializers import IdeaDetailSerializer
from apps.userpage.models import UserProfile
from apps.search.serializers import UniformIndexSerializer, UserIndexSerializer
from apps.utils.api import CustomAPIView


class RootView(ViewSetMixin, HaystackGenericAPIView, CustomAPIView):
    index_models = [Question, Answer, Article, Idea]
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
        articles = Article.objects.filter(id__in=temp.get("article", []))
        ideas = Idea.objects.filter(id__in=temp.get("idea", []))

        data1 = self.paginate_data(request, questions, NewQuestionSerializer, serializer_context={"me": me})
        data2 = self.paginate_data(request, answers, AnswerCreateSerializer, serializer_context={"me": me})
        data3 = self.paginate_data(request, articles, ArticleDetailSerializer, serializer_context={"me": me})
        data4 = self.paginate_data(request, ideas, IdeaDetailSerializer, serializer_context={"me": me})
        data = {
            "questions": data1,
            "answers": data2,
            "articles": data3,
            "ideas": data4,
            "total": len(queryset),

        }
        return self.success(data)


class FindUserView(ViewSetMixin, HaystackGenericAPIView, CustomAPIView):
    index_models = [UserProfile]
    serializer_class = UserIndexSerializer

    def list(self, request):
        me = self.get_user_profile(request)
        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_data(request, queryset, self.get_serializer_class())
        return self.success(data)
