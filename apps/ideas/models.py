from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Idea(models.Model):
    user_id = models.CharField(max_length=40, null=False, verbose_name="提出者ID")
    content = models.TextField(null=False, blank=False, verbose_name="想法内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="提出时间")
    agree = GenericRelation(to="IdeaAgree", verbose_name="想法点赞")

    class Meta:
        db_table = "db_thinks"
        verbose_name = "想法"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class IdeaComment(models.Model):
    user_id = models.CharField(max_length=40, null=False, verbose_name="评论者ID")
    think = models.ForeignKey(to="Idea", null=False, blank=False, verbose_name="想法ID")
    content = models.TextField(null=False, blank=False, verbose_name="想法评论内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    agree = GenericRelation(to="IdeaAgree", verbose_name="想法点赞")

    class Meta:
        db_table = "db_think_comments"
        verbose_name = "想法评论"
        verbose_name_plural = verbose_name


class IdeaAgree(models.Model):
    user_id = models.CharField(max_length=40, null=False, verbose_name="点赞者ID")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")
    content_type = models.ForeignKey(to=ContentType, null=False, blank=False, verbose_name="点赞对象类型")
    object_id = models.CharField(max_length=40, null=False, blank=False, verbose_name="点赞对象ID")
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_tc_like"
        verbose_name = "想法评论点赞"
        verbose_name_plural = verbose_name
        unique_together = ("user_id", "content_type", "object_id")  # 不能重复点赞
