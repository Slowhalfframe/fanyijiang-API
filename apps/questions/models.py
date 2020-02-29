from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from apps.labels.models import Label

# 引入收藏夹内容模型
from apps.userpage.models import FavoriteCollection
from apps.creator.models import ReadNums

class ACVote(models.Model):
    """对回答或问答的评论的投票，不能重复投票"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="投票者ID")
    value = models.BooleanField(null=False, verbose_name="投票值")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="投票时间")
    content_type = models.ForeignKey(to=ContentType, verbose_name="被评论对象的类型")
    object_id = models.CharField(max_length=20, null=False, verbose_name="被评论对象的ID")
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_ac_vote"
        verbose_name = "问答和评论投票"
        verbose_name_plural = verbose_name
        unique_together = (("user_id", "object_id", "content_type"),)  # 禁止重复投票


class QAComment(models.Model):
    """对问题和回答的评论"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="评论者ID")
    content = models.TextField(null=False, verbose_name="评论内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    reply_to_user = models.CharField(max_length=40, null=True, verbose_name="被评论用户ID")
    vote = GenericRelation(to=ACVote)
    content_type = models.ForeignKey(to=ContentType, verbose_name="被评论对象的类型")
    object_id = models.CharField(max_length=20, null=False, verbose_name="被评论对象的ID")
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_qa_comments"
        verbose_name = "问答的评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]


class Question(models.Model):
    """问题，标题不能重复"""
    title = models.CharField(max_length=100, null=False, unique=True, verbose_name="问题标题")
    content = models.TextField(null=True, blank=True, default="", verbose_name="问题描述")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")
    labels = models.ManyToManyField(to=Label, verbose_name="问题的标签")
    user_id = models.CharField(max_length=40, null=False, verbose_name="提问者ID")
    comment = GenericRelation(to=QAComment)

    class Meta:
        db_table = "db_questions"
        verbose_name = "问题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Answer(models.Model):
    """问题的回答，同一用户不能重复回答同一问题"""
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题ID")
    content = models.TextField(null=False, verbose_name="回答内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="回答时间")
    user_id = models.CharField(max_length=40, null=False, verbose_name="回答者ID")
    vote = GenericRelation(to=ACVote)
    comment = GenericRelation(to=QAComment)
    # 添加收藏关系
    collect = GenericRelation(to=FavoriteCollection)

    read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "db_answers"
        verbose_name = "回答"
        verbose_name_plural = verbose_name
        unique_together = (("question", "user_id"),)  # 用户回答问题后不能再次回答，但可以修改

    def __str__(self):
        return self.content[:20]


class QuestionFollow(models.Model):
    """关注的问题"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="关注者ID")
    question = models.ForeignKey(to=Question, null=False, verbose_name="关注的问题")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        db_table = "db_q_follows"
        verbose_name = "问题关注"
        verbose_name_plural = verbose_name
        unique_together = (("user_id", "question"),)  # 不能重复关注


class QuestionInvite(models.Model):
    """邀请回答"""
    STATUS = (
        (0, "未回答"),
        (1, "已拒绝"),
        (2, "已回答"),
    )
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="邀请时间")
    inviting = models.CharField(max_length=40, null=False, verbose_name="邀请者ID")
    invited = models.CharField(max_length=40, null=False, verbose_name="被邀请者ID")
    status = models.SmallIntegerField(choices=STATUS, null=False, verbose_name="状态")

    class Meta:
        db_table = "db_q_invite"
        verbose_name = "邀请回答"
        verbose_name_plural = verbose_name
        unique_together = (("question", "inviting", "invited",),)  # 不能重复邀请
