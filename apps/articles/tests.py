from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels.models import Label
from .models import Article


def prepare(obj):
    common_prepare(obj)
    obj.label = Label.objects.create(name="标签1")
    obj.article = Article.objects.create(title="标题1", content="内容1", is_draft=True, author=obj.users["zhang"])
    obj.article.labels.add(obj.label)


class ArticleViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.path = reverse("articles:root")
        self.data = {
            "title": "标题1",
            "content": "内容1",
            "is_draft": True,
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
        self.data["is_draft"] = "None"
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_labels(self):
        self.data.pop("labels")
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class OneArticleViewDeleteTest(TestCase):
    def setUp(self):
        prepare(self)
        self.path = reverse("articles:one_article", kwargs={"article_id": self.article.pk})

    def test_no_login(self):
        response = self.client.delete(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_not_exist(self):
        path = reverse("articles:one_article", kwargs={"article_id": self.article.pk + 1})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_not_your_article(self):
        self.article.author = self.users["euler"]
        self.article.save()
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_draft(self):
        me = self.users["zhang"]
        self.assertEqual(Article.objects.filter(author=me).count(), 1)
        self.assertEqual(Article.objects.filter(author=me, is_draft=True).count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(Article.objects.filter(author=me).count(), 0)

    def test_article_published(self):
        self.article.is_draft = False
        self.article.save()
        me = self.users["zhang"]
        self.assertEqual(Article.objects.filter(author=me).count(), 1)
        self.assertEqual(Article.objects.filter(author=me, is_draft=False).count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(Article.objects.filter(author=me).count(), 1)
        self.assertEqual(Article.objects.filter(author=me, is_draft=False).count(), 1)
        self.assertTrue(Article.objects.filter(author=me).first().is_deleted)


class OneArticleViewPutTest(TestCase):
    def setUp(self):
        prepare(self)
        self.path = reverse("articles:one_article", kwargs={"article_id": self.article.pk})
        self.data = {
            "title": "标题2",
            "content": "内容2",
            "is_draft": True,
            "labels": self.label.pk
        }

    def test_no_login(self):
        response = self.client.put(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_not_exist(self):
        path = reverse("articles:one_article", kwargs={"article_id": self.article.pk + 1})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_not_your_article(self):
        self.article.author = self.users["gauss"]
        self.article.save()
        response = self.client.put(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_published_to_draft(self):
        self.article.is_draft = False
        self.article.save()
        response = self.client.put(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class DraftViewPostTest(TestCase):
    def setUp(self):
        prepare(self)
        self.path = reverse("articles:draft_root")
        self.data = {"id": self.article.pk}

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_not_exist(self):
        data = {"id": self.article.pk + 1}
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_not_your_article(self):
        self.article.author = self.users["gauss"]
        self.article.save()
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_not_draft(self):
        self.article.is_draft = False
        self.article.save()
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class ArticleFollowViewPostTest(TestCase):
    def setUp(self):
        prepare(self)
        self.article.is_draft = False
        self.article.save()
        self.path = reverse("articles:follow", kwargs={"article_id": self.article.pk})

    def test_no_login(self):
        response = self.client.post(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_not_exist(self):
        path = reverse("articles:follow", kwargs={"article_id": self.article.pk + 1})
        response = self.client.post(path, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_article_is_draft(self):
        self.article.is_draft = True
        self.article.save()
        response = self.client.post(self.path, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class ArticleFollowViewDeleteTest(TestCase):
    def setUp(self):
        prepare(self)
        self.article.is_draft = False
        self.article.save()
        self.path = reverse("articles:follow", kwargs={"article_id": self.article.pk})

    def test_no_login(self):
        response = self.client.delete(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
