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
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_answer_not_exist(self):
        path = reverse("votes:root", kwargs={"kind": "answer", "id": self.answer.pk + 1})
        self.assertFalse(Answer.objects.filter(pk=self.answer.pk + 1).exists())
        response = self.client.post(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_answer_is_draft(self):
        self.answer.is_draft = True
        self.answer.save()
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_have_voted(self):
        Vote.objects.create(content_object=self.answer, author=self.users["zhang"], value=True)
        self.assertEqual(self.answer.votes.count(), 1)
        self.assertTrue(self.answer.votes.first().value)
        data = {"value": False}
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.answer.votes.count(), 1)
        self.assertFalse(self.answer.votes.first().value)

    def test_vote_to_yourself(self):
        self.answer.author = self.users["zhang"]
        self.answer.save()
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.answer.votes.count(), 1)
        self.assertTrue(self.answer.votes.first().value)

    def test_no_value(self):
        data = {"value": None}
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class VoteViewDeleteTest(TestCase):
    def setUp(self):
        prepare(self)
        self.answer.votes.create(author=self.users["zhang"], value=True)

    def test_no_login(self):
        response = self.client.delete(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_have_voted(self):
        self.assertEqual(self.answer.votes.filter(author=self.users["zhang"]).count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.answer.votes.filter(author=self.users["zhang"]).count(), 0)

    def test_have_not_voted(self):
        self.answer.votes.all().delete()
        self.assertEqual(self.answer.votes.filter(author=self.users["zhang"]).count(), 0)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
