from haystack import indexes

from .models import Question, Answer


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    content = indexes.CharField(model_attr="content")

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
