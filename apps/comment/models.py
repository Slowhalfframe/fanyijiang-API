from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel


class Comment(BaseModel):
    """评论，适用于问题、问题的回答、文章、想法等，以及评论的评论"""

    content = models.TextField(null=False, blank=False, verbose_name="评论内容")
    author = models.ForeignKey(to=UserProfile, null=False, blank=False, verbose_name="评论者")
    content_type = models.ForeignKey(to=ContentType, null=False, verbose_name="被评论对象的类型")
    object_id = models.PositiveIntegerField(null=False, verbose_name="被评论对象的主键")
    content_object = GenericForeignKey("content_type", "object_id")
    comments = GenericRelation(to="self")  # 用于获取评论的子评论
    votes = GenericRelation(to="Vote")  # 用于获取评论的投票

    class Meta:
        db_table = "comment"
        verbose_name = "评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]

    @property
    def kind(self):
        return "comment"

    @property
    def respondent(self):
        """被回复者"""

        return self.content_object.author

    @property
    def root_object(self):
        """被评论的根对象，即问答、文章、想法等"""

        root = self.content_object
        while isinstance(root, Comment):
            root = root.content_object
        return root


class Vote(BaseModel):
    """投票，泛指各种取True或False但不存在时应看作None的事物，操作时注意不能重复投票"""

    value = models.BooleanField(null=False, blank=False, verbose_name="赞成还是反对")
    author = models.ForeignKey(to=UserProfile, null=False, blank=False, verbose_name="投票者")
    content_type = models.ForeignKey(to=ContentType, null=False, verbose_name="被投票对象的类型")
    object_id = models.PositiveIntegerField(null=False, verbose_name="被投票对象的主键")
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "vote"
        verbose_name = "投票"
        verbose_name_plural = verbose_name
