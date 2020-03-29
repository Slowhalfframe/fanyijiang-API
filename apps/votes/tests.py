from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label
from apps.questions_v2.models import Question, Answer
from .models import Vote


def prepare(obj):
    """以回答投票为例进行准备"""

    common_prepare(obj)
    obj.label = Label.objects.create(name="标签1")
    obj.question = Question.objects.create(title="问题1", author=obj.users["zhao"])
    obj.question.labels.add(obj.label)
    obj.answer = Answer.objects.create(author=obj.users["zhao"], question=obj.question, content="回答1", is_draft=False)
    obj.path = reverse("votes:root", kwargs={"kind": "answer", "id": obj.answer.pk})
    obj.data = {"value": True}


class VoteViewPostTest(TestCase):
    def setUp(self):
        prepare(self)

    def test_no_login(self):
        pass

    def test_answer_not_exist(self):
        pass

    def test_answer_is_draft(self):
        pass

    def test_have_voted(self):
        pass


class VoteViewDeleteTest(TestCase):
    def setUp(self):
        prepare(self)
        self.answer.votes.create(author=self.users["zhao"], value=True)

    def test_no_login(self):
        pass

    def test_not_your_vote(self):
        pass

    def test_have_voted(self):
        pass

    def test_have_not_voted(self):
        pass
