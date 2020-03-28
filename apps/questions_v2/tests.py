from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from apps.labels_v2.models import Label
from .models import Question, Answer


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

    def test_no_label(self):
        data = self.data.copy()
        data["labels"] = [self.label1.pk + self.label2.pk]
        self.assertEqual(Question.objects.count(), 0)
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        self.assertEqual(Question.objects.count(), 0)


class OneQuestionViewPutTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label1 = Label.objects.create(name="标签1")
        self.label2 = Label.objects.create(name="标签2")
        self.question = Question.objects.create(title="问题1", content="内容1", author=self.users["zhang"])
        self.question.labels.add(self.label1)
        self.data = {"title": "问题标题", "content": "进一步描述", "labels": [self.label1.pk, self.label2.pk]}
        self.path = reverse("questions_v2:one_question", kwargs={"question_id": self.question.pk})

    def test_no_login(self):
        response = self.client.put(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_question_not_exist(self):
        path = reverse("questions_v2:one_question", kwargs={"question_id": self.question.pk + 1})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_not_author(self):
        question = Question.objects.create(title="问题2", content="内容2", author=self.users["zhao"])
        question.labels.add(self.label2)
        self.assertEqual(Question.objects.count(), 2)
        path = reverse("questions_v2:one_question", kwargs={"question_id": question.pk})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_label(self):
        data = self.data.copy()
        data["labels"] = [self.label1.pk + self.label2.pk]
        response = self.client.put(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        self.assertEqual(self.question.labels.count(), 1)

    def test_title_unchanged(self):
        data = self.data.copy()
        data["title"] = self.question.title
        response = self.client.put(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class AnswerViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.question = Question.objects.create(title="标题1", content="内容1", author=self.users["zhao"])
        self.question.labels.add(self.label)
        self.data = {"content": "回答1", "is_draft": True}
        self.path = reverse("questions_v2:answer_root", kwargs={"question_id": self.question.pk})

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_question_not_exist(self):
        path = reverse("questions_v2:answer_root", kwargs={"question_id": self.question.pk + 1})
        self.assertIs(Question.objects.filter(pk=self.question.pk + 1).exists(), False)
        response = self.client.post(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_is_question_author(self):
        question = Question.objects.create(title="标题2", content="内容2", author=self.users["zhang"])
        path = reverse("questions_v2:answer_root", kwargs={"question_id": question.pk})
        response = self.client.post(path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_only_draft_answer(self):
        Answer.objects.create(author=self.users["zhang"], question=self.question, **self.data)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 1)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 0)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 2)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 0)
        data = self.data.copy()
        data["is_draft"] = False
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 1)

    def test_have_published_answer(self):
        Answer.objects.create(author=self.users["zhang"], question=self.question, content="回答1", is_draft=False)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 1)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 1)


class OneAnswerViewDeleteTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.question = Question.objects.create(title="问题1", author=self.users["zhao"])
        self.question.labels.add(self.label)
        self.answer = Answer.objects.create(content="回答1", question=self.question, author=self.users["zhang"],
                                            is_draft=True)
        self.path = reverse("questions_v2:one_answer",
                            kwargs={"question_id": self.question.pk, "answer_id": self.answer.pk})

    def test_no_login(self):
        response = self.client.delete(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_question_or_answer_not_exist(self):
        path = reverse("questions_v2:one_answer",
                       kwargs={"question_id": self.question.pk + 1, "answer_id": self.answer.pk})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        path = reverse("questions_v2:one_answer",
                       kwargs={"question_id": self.question.pk, "answer_id": self.answer.pk + 1})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_not_author(self):
        answer = Answer.objects.create(content="回答2", question=self.question, author=self.users["zhao"], is_draft=False)
        path = reverse("questions_v2:one_answer",
                       kwargs={"question_id": self.question.pk, "answer_id": answer.pk})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_delete_draft(self):
        self.assertEqual(self.question.answer_set.count(), 1)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.count(), 0)

    def test_delete_published(self):
        self.answer.is_draft = False
        self.answer.save()
        self.assertEqual(self.question.answer_set.count(), 1)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.count(), 1)
        self.assertEqual(self.question.answer_set.filter(is_draft=False, is_deleted=True).count(), 1)


class OneAnswerViewPutTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.question = Question.objects.create(title="问题1", author=self.users["zhao"])
        self.question.labels.add(self.label)
        self.answer = Answer.objects.create(content="回答1", question=self.question, author=self.users["zhang"],
                                            is_draft=True)
        self.path = reverse("questions_v2:one_answer",
                            kwargs={"question_id": self.question.pk, "answer_id": self.answer.pk})
        self.data = {"content": "回答2", "is_draft": True}

    def test_no_login(self):
        response = self.client.put(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_question_or_answer_not_exist(self):
        path = reverse("questions_v2:one_answer",
                       kwargs={"question_id": self.question.pk + 1, "answer_id": self.answer.pk})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        path = reverse("questions_v2:one_answer",
                       kwargs={"question_id": self.question.pk, "answer_id": self.answer.pk + 1})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_not_author(self):
        self.answer.author = self.users["zhao"]
        self.answer.save()
        response = self.client.put(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_published_to_draft(self):
        self.answer.is_draft = False
        self.answer.save()
        response = self.client.put(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_draft_to_published(self):
        Answer.objects.create(content="又一篇草稿", question=self.question, author=self.users["zhang"], is_draft=True)
        self.assertEqual(self.question.answer_set.count(), 2)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 2)
        self.data["is_draft"] = False
        response = self.client.put(self.path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=True).count(), 0)
        self.assertEqual(self.question.answer_set.filter(is_draft=False).count(), 1)
