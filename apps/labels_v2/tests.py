import requests
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from apps.userpage.models import UserProfile


class LabelViewPostTest(TestCase):
    def setUp(self):
        UserProfile.objects.create(uid="e4da3b7fbbce2345d7772b0674a318d5", nickname="haoran·zhang", slug="zhanghaoran")
        UserProfile.objects.create(uid="a87ff679a2f3e71d9181a67b7542122c", nickname="赵军臣", slug="zhao-jun-chen")
        self.path = reverse("labels_v2:root")
        data = {
            "username": "18569938068",
            "password": "1234567",
            "login_type": "normal"
        }
        response = requests.post(settings.USER_CENTER_GATEWAY + "/api/login", data=data)
        self.headers = {"HTTP_AUTHORIZATION": response.json()["data"]["token"]}
        self.data = {"name": "标签", "intro": "好", "avatar": "/pub/3.png"}
        self.client = Client()

    def tearDown(self):
        pass

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
        response = self.client.post(self.path, data={"name": "<", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, data={"name": ">", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, data={"name": "&", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
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
