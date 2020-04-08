from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel


class Vote(BaseModel):
    """投票，泛指各种取True或False但不存在时应看作None的事物，操作时注意不能重复投票"""

    value = models.BooleanField(null=False, blank=False, verbose_name="赞成还是反对")
    author = models.ForeignKey(to=UserProfile, null=False, blank=False, verbose_name="投票者")
    content_type = models.ForeignKey(to=ContentType, null=False, verbose_name="被投票对象的类型")
    object_id = models.PositiveIntegerField(null=False, verbose_name="被投票对象的主键")
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "db_vote"
        verbose_name = "投票"
        verbose_name_plural = verbose_name
