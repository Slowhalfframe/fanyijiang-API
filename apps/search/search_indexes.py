from haystack import indexes

from apps.questions.models import Question, Answer


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
