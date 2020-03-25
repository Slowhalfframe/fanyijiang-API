import requests
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.userpage.models import UserProfile
from .models import Label


def common_prepare(obj):
    """准备测试用户、登录和客户端"""

    UserProfile.objects.create(uid="e4da3b7fbbce2345d7772b0674a318d5", nickname="haoran·zhang", slug="zhanghaoran")
    UserProfile.objects.create(uid="a87ff679a2f3e71d9181a67b7542122c", nickname="赵军臣", slug="zhao-jun-chen")
    data = {
        "username": "18569938068",
        "password": "1234567",
        "login_type": "normal"
    }
    response = requests.post(settings.USER_CENTER_GATEWAY + "/api/login", data=data)
    obj.headers = {"HTTP_AUTHORIZATION": response.json()["data"]["token"]}
    obj.client = APIClient()


class LabelViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.path = reverse("labels_v2:root")
        self.data = {"name": "标签", "intro": "好", "avatar": "/pub/3.png"}

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_name(self):
        data = self.data.copy()
        data.pop("name")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_name_is_none(self):
        data = self.data.copy()
        data["name"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_empty_name(self):
        data = self.data.copy()
        data["name"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_bad_name(self):
        response = self.client.post(self.path, {"name": "<", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, {"name": ">", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, {"name": "&", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_name_exist(self):
        Label.objects.create(**self.data)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_intro(self):
        data = self.data.copy()
        data.pop("intro")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_intro_is_none(self):
        data = self.data.copy()
        data["intro"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_empty_intro(self):
        data = self.data.copy()
        data["intro"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_intro_with_html(self):
        data = self.data.copy()
        data["intro"] = "<p>OK</p>"
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["intro"], "&lt;p&gt;OK&lt;/p&gt;")

    def test_no_avatar(self):
        data = self.data.copy()
        data.pop("avatar")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_avatar_is_none(self):
        data = self.data.copy()
        data["avatar"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_empty_avatar(self):
        data = self.data.copy()
        data["avatar"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_bad_avatar(self):
        data = self.data.copy()
        data["avatar"] = "afd/1.pn"
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class OneLabelViewDeleteTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(**{"name": "标签", "intro": "好", "avatar": "/pub/3.png"})

    def test_label_not_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk + 1})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_label_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class OneLabelViewPutTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.old_data = {"name": "标签", "intro": "好", "avatar": "/pub/3.png"}
        self.label = Label.objects.create(**self.old_data)
        self.data = {"name": "新标签", "intro": "新说明", "avatar": "/pub/12.jpg"}

    def test_no_login(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.put(path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_not_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk + 1})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["name"], self.data["name"])
        self.assertEqual(data["data"]["intro"], self.data["intro"])
        self.assertEqual(data["data"]["avatar"], self.data["avatar"])

    def test_label_name_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        data = self.data.copy()
        data["name"] = self.old_data["name"]
        response = self.client.put(path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class ChildLabelViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        Label.objects.create(name="标签1")
        Label.objects.create(name="标签2")
        self.path = reverse("labels_v2:child", kwargs={"label_id": 1})

    def test_no_login(self):
        response = self.client.post(self.path, {"id": 2})
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_parent(self):
        path = reverse("labels_v2:child", kwargs={"label_id": 3})
        response = self.client.post(path, {"id": 2}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_child(self):
        response = self.client.post(self.path, {"id": 3}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_ok(self):
        response = self.client.post(self.path, {"id": 2}, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
