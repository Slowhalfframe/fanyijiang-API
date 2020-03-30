from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label


class ArticleViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.path = reverse("articles_v2:root")
        self.data = {
            "title": "标题1",
            "content": "内容1",
            "status": "draft",
            "labels": self.label.pk
        }

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_title(self):
        self.data.pop("title")
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_content(self):
        self.data.pop("content")
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_bad_status(self):
        self.data["status"] = "Draft"
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_labels(self):
        self.data.pop("labels")
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
