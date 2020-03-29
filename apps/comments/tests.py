from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label
from apps.questions_v2.models import Question, Answer


def prepare(obj):
    """以回答评论为例进行准备"""

    common_prepare(obj)
    obj.label = Label.objects.create(name="标签1")
    obj.question = Question.objects.create(title="问题1", author=obj.users["zhao"])
    obj.question.labels.add(obj.label)
    obj.answer = Answer.objects.create(author=obj.users["zhao"], question=obj.question, content="回答1", is_draft=False)
    obj.path = reverse("comments:root", kwargs={"kind": "answer", "id": obj.answer.pk})
    obj.data = {"content": "评论1"}


class CommentViewPostTest(TestCase):
    def setUp(self):
        prepare(self)

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_answer_not_exist(self):
        path = reverse("comments:root", kwargs={"kind": "answer", "id": self.answer.pk + 1})
        response = self.client.post(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_have_commented(self):
        self.answer.comments.create(author=self.users["zhang"], **self.data)
        self.assertEqual(self.answer.comments.count(), 1)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.answer.comments.count(), 2)

    def test_comment_a_comment(self):
        comment = self.answer.comments.create(author=self.users["zhao"], **self.data)
        self.assertEqual(self.answer.comments.count(), 1)
        path = reverse("comments:root", kwargs={"kind": "comment", "id": comment.pk})
        data = {"content": "评论1的子评论1"}
        response = self.client.post(path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(comment.comments.count(), 1)

    def test_comment_a_draft(self):
        self.answer.is_draft = True
        self.answer.save()
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
