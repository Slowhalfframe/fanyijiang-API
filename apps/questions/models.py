from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from apps.labels.models import Label


class ACVote(models.Model):
    """对问题的回答及其评论的投票"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="投票者ID")
    value = models.BooleanField(null=False, verbose_name="投票值")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="投票时间")
    content_type = models.ForeignKey(to=ContentType, null=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_ac_vote"
        verbose_name = "对回答及其评论的投票"
        verbose_name_plural = verbose_name
        unique_together = (("user_id", "object_id", "content_type"),)  # 禁止重复投票


class QAComment(models.Model):
    """对问题和回答的评论"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="评论者ID")
    content = models.TextField(null=False, verbose_name="评论内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    reply_to_user = models.CharField(max_length=40, null=True, verbose_name="被回复用户ID")
    vote = GenericRelation(to=ACVote, null=False)
    content_type = models.ForeignKey(to=ContentType, null=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_qa_comments"
        verbose_name = "问答的评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]


class Question(models.Model):
    title = models.CharField(max_length=100, null=False, unique=True, verbose_name="问题标题")  # 不能重复提问
    content = models.TextField(null=False, verbose_name="问题描述")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")
    labels = models.ManyToManyField(to=Label, verbose_name="问题的标签")
    user_id = models.CharField(max_length=40, null=False, blank=False, verbose_name="提问者ID")
    comment = GenericRelation(to=QAComment)

    class Meta:
        db_table = "db_questions"
        verbose_name = "问题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题ID")
    content = models.TextField(null=False, verbose_name="回答内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="回答时间")
    user_id = models.CharField(max_length=40, null=False, blank=False, verbose_name="回答者ID")
    vote = GenericRelation(to=ACVote)
    comment = GenericRelation(to=QAComment)

    class Meta:
        db_table = "db_answers"
        verbose_name = "回答"
        verbose_name_plural = verbose_name
        unique_together = (("question", "user_id"),)  # 用户回答问题后不能再次回答，但可以修改

    def __str__(self):
        return self.content[:20]
