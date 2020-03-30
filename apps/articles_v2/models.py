from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.comments.models import Comment
from apps.labels_v2.models import Label
from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel
from apps.votes.models import Vote


class Article(BaseModel):
    """文章，同一作者可以发表多篇同一标题的文章，尽管这几乎不会发生"""

    STATUS = (("draft", "draft"), ("published", "published"))

    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="文章标题")
    content = models.TextField(null=False, blank=False, verbose_name="文章主体")
    thumbnail = models.CharField(max_length=100, null=True, verbose_name="缩略图路径")
    status = models.CharField(max_length=10, choices=STATUS, null=False, blank=False, verbose_name="状态")
    author = models.ForeignKey(to=UserProfile, null=False, blank=False, verbose_name="作者")
    labels = models.ManyToManyField(to=Label, verbose_name="文章的标签")
    comments = GenericRelation(to=Comment)
    votes = GenericRelation(to=Vote)

    # mark = GenericRelation(to=FavoriteCollection, verbose_name="收藏")
    # read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "article"
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    @property
    def kind(self):
        return "answer"
