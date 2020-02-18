from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.QuestionView.as_view(), name="questions"),
    url(r"^(?P<question_id>\d+)/answers/$", views.AnswerView.as_view(), name="answers"),
]
