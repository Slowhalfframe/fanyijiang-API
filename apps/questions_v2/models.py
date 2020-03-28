from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.comments.models import Comment, Vote
from apps.labels_v2.models import Label
from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel


class Question(BaseModel):
    """问题，标题不能重复"""

    title = models.CharField(max_length=100, unique=True, null=False, blank=False, verbose_name="问题标题")
    content = models.TextField(null=True, blank=True, verbose_name="问题描述")
    author = models.ForeignKey(to=UserProfile, null=False, verbose_name="提问者")
    labels = models.ManyToManyField(to=Label, verbose_name="问题的标签")
    comments = GenericRelation(to=Comment)

    # read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "question"
        verbose_name = "问题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    @property
    def kind(self):
        return "question"


class Answer(BaseModel):
    """问题的回答，每个问题每个用户只能正式回答一次，但可以修改或有多个草稿"""

    content = models.TextField(null=False, blank=False, verbose_name="回答内容")
    is_draft = models.BooleanField(null=False, blank=False, verbose_name="是否是草稿")
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题")
    author = models.ForeignKey(to=UserProfile, null=False, verbose_name="回答者")
    comments = GenericRelation(to=Comment)
    votes = GenericRelation(to=Vote)

    # # 添加收藏关系
    # collect = GenericRelation(to=FavoriteCollection)
    # read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "answer"
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]

    @property
    def kind(self):
        return "answer"


'''
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

'''
