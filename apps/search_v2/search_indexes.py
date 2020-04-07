from haystack import indexes

from apps.questions_v2.models import Question, Answer
from apps.articles_v2.models import Article
from apps.pins.models import Idea
from apps.userpage_v2.models import UserProfile


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr="id")
    kind = indexes.CharField(default="question")

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class AnswerIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr="id")
    kind = indexes.CharField(default="answer")

    def get_model(self):
        return Answer

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr="id")
    kind = indexes.CharField(default="article")

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_deleted=False, status="published")


class IdeaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr="id")
    kind = indexes.CharField(default="idea")

    def get_model(self):
        return Idea

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # uid = indexes.CharField(model_attr="uid")
    # kind = indexes.CharField(default="user")

    def get_model(self):
        return UserProfile

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
