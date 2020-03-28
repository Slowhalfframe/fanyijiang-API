from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.QuestionView.as_view(), name="root"),
    url(r"^(?P<question_id>\d+)/$", views.OneQuestionView.as_view(), name="one_question"),
    url(r"^(?P<question_id>\d+)/answers/$", views.AnswerView.as_view(), name="answer_root"),
]
