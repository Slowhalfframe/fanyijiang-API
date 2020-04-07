from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.comments.models import Comment
from apps.userpage_v2.models import UserProfile
from apps.utils_v2.models import BaseModel
from apps.votes.models import Vote


class Idea(BaseModel):
    """想法"""

    content = models.TextField(null=False, blank=False, verbose_name="想法内容")
    # 想法的配图，最多9张
    # 保存的是各图片的路径的列表经过JSON编码后的字符串
    # 默认值是空列表经过JSON编码后的字符串，因为空字符串在JSON解码时会出错
    avatars = models.CharField(max_length=800, null=False, blank=False, default="[]", verbose_name="配图路径")
    author = models.ForeignKey(to=UserProfile, null=False, verbose_name="作者")
    comments = GenericRelation(to=Comment)
    votes = GenericRelation(to=Vote)  # 想法的点赞即投票，不过只有未投票和赞成票两种

    # read_nums = GenericRelation(to=ReadNums)
    # collect = GenericRelation(to=FavoriteCollection)

    class Meta:
        db_table = "idea"
        verbose_name = "想法"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    @property
    def kind(self):
        return "idea"

    @property
    def url(self):
        return "/pins/" + str(self.id)
