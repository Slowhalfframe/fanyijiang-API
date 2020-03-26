from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label
from apps.questions_v2.models import Question


class QuestionViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label1 = Label.objects.create(name="标签1")
        self.label2 = Label.objects.create(name="标签2")
        self.path = reverse("questions_v2:root")
        self.data = {"title": "问题标题", "content": "进一步描述", "labels": [self.label1.pk, self.label2.pk]}

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_title_exist(self):
        self.assertEqual(Question.objects.count(), 0)
        self.client.post(self.path, self.data, **self.headers)
        self.assertEqual(Question.objects.count(), 1)
        data = self.data.copy()
        data["content"] = "不同的内容"
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        self.assertEqual(Question.objects.count(), 1)
