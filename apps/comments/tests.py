from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label
from apps.questions_v2.models import Question


def prepare(obj):
    """以问题评论为例进行准备"""

    common_prepare(obj)
    obj.label = Label.objects.create(name="标签1")
    obj.question = Question.objects.create(title="问题1", author=obj.users["zhao"])
    obj.question.labels.add(obj.label)
    obj.path = reverse("comments:root", kwargs={"kind": "question", "id": obj.question.pk})
    obj.data = {"content": "评论1"}


class CommentViewPostTest(TestCase):
    def setUp(self):
        prepare(self)

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_question_not_exist(self):
        path = reverse("comments:root", kwargs={"kind": "question", "id": self.question.pk + 1})
        response = self.client.post(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_have_commented(self):
        self.question.comments.create(author=self.users["zhang"], **self.data)
        self.assertEqual(self.question.comments.count(), 1)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.comments.count(), 2)
