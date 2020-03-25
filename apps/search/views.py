from drf_haystack.generics import HaystackGenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from apps.questions.models import Question, Answer
from apps.questions.serializers import NewQuestionSerializer, SearchAnswersSerializer
from apps.articles.models import Article
from apps.articles.serializers import ArticleDetailSerializer
from apps.ideas.models import Idea
from apps.ideas.serializers import IdeaDetailSerializer
from apps.userpage.models import UserProfile
from apps.userpage.serializers import FollowsUserSerializer
from apps.search.serializers import UniformIndexSerializer, UserIndexSerializer
from apps.utils.api import CustomAPIView


class RootView(ViewSetMixin, HaystackGenericAPIView, CustomAPIView):
    index_models = [Question, Answer, Article, Idea]
    serializer_class = UniformIndexSerializer

    def list(self, request):
        # TODO 从request.GET获取搜索关键字并记录
        me = self.get_user_profile(request)
        queryset = self.filter_queryset(self.get_queryset())
        result = []
        mapping = {
            Question.__name__: NewQuestionSerializer,
            Answer.__name__: SearchAnswersSerializer,
            Article.__name__: ArticleDetailSerializer,
            Idea.__name__: IdeaDetailSerializer
        }
        for i in queryset:
            instance = i.object
            if isinstance(instance,Answer):
                s = mapping[instance.__class__.__name__](instance={"answer":instance}, context={"me": me})
            else:
                s = mapping[instance.__class__.__name__](instance=instance, context={"me": me})
            data = dict(s.data)
            data["kind"] = instance.__class__.__name__.lower()
            result.append(data)


        data = {"result": result, "total": len(queryset)}
        return self.success(data)


class FindUserView(ViewSetMixin, HaystackGenericAPIView, CustomAPIView):
    index_models = [UserProfile]
    serializer_class = FollowsUserSerializer

    def list(self, request):
        me = self.get_user_profile(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = [i.object for i in queryset]
        data = self.paginate_data(request, queryset, self.get_serializer_class())
        if not me:
            for r in data["results"]:
                r["is_idol"] = False
        else:
            for r in data["results"]:
                r["is_idol"] = UserProfile.objects.filter(as_idol__fans__uid=me.uid, slug=r['slug']).exists()
        return self.success(data)
