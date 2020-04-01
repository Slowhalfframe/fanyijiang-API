import json

from django.test import TestCase
from django.urls import reverse

from apps import common_prepare


class IdeaViewTestPost(TestCase):
    def setUp(self):
        common_prepare(self)
        self.path = reverse("pins:root")
        self.data = {
            "content": "绝妙的想法",
            "avatars": "[]",
        }

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_avatars_are_json_str(self):
        self.data["avatars"] = json.dumps(["/home/qiaofeng/1.png", "/home/qiaofeng/2.jpg"])
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_avatars_are_comma_separated_paths(self):
        self.data["avatars"] = "/home/qiaofeng/1.png,/home/qiaofeng/2.jpg"
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
