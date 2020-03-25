from django.db import models

from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel


class Label(BaseModel):
    """标签，或者称作话题，名称不可重复"""

    name = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="标签名称")
    intro = models.TextField(null=True, blank=True, verbose_name="标签介绍")
    avatar = models.CharField(max_length=100, blank=True, null=True, verbose_name="标签头像")
    children = models.ManyToManyField(to="self", symmetrical=False, verbose_name="子标签", related_name="parents")

    class Meta:
        db_table = "label"
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class LabelFollow(BaseModel):
    """用户与标签的多对多关注关系"""

    user = models.ForeignKey(to=UserProfile, null=False, verbose_name="关注者ID")
    label = models.ForeignKey(to=Label, null=False, verbose_name="关注的标签")

    class Meta:
        db_table = "label_follow"
        verbose_name = "标签关注"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "".join((self.user.nickname, "跟踪了", self.label.name))
