from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.labels.models import Label
from apps.userpage.models import FavoriteCollection

from apps.creator.models import ReadNums


class Article(models.Model):
    STATUS = (("draft", "draft"), ("published", "published"))
    user_id = models.CharField(max_length=40, null=False, verbose_name="作者ID")
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="文章标题")
    content = models.TextField(null=False, blank=False, verbose_name="文章正文")
    image = models.CharField(max_length=100, null=True, blank=True, verbose_name="缩略图路径")
    status = models.CharField(max_length=10, choices=STATUS, null=False, blank=True, default="draft",
                              verbose_name="草稿或成品")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_deleted = models.BooleanField(null=False, blank=True, verbose_name="逻辑删除", default=False)
    labels = models.ManyToManyField(to=Label, verbose_name="文章的标签")
    vote = GenericRelation(to="ArticleVote", verbose_name="文章投票")
    # TODO 阅读量
    mark = GenericRelation(to=FavoriteCollection, verbose_name="收藏")

    # 阅读量
    read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "db_articles"
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ArticleComment(models.Model):
    article = models.ForeignKey(to="Article", null=False, blank=False, verbose_name="被评论文章")
    user_id = models.CharField(max_length=40, null=False, verbose_name="评论者ID")
    content = models.TextField(null=False, blank=False, verbose_name="评论内容")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    reply_to_user = models.CharField(max_length=40, null=True, blank=True, verbose_name="被评论者ID")
    vote = GenericRelation(to="ArticleVote", verbose_name="评论投票")

    class Meta:
        db_table = "db_article_comments"
        verbose_name = "文章评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class ArticleVote(models.Model):
    """文章及其评论的投票"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="投票者ID")
    value = models.BooleanField(null=False, verbose_name="投票值")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="投票时间")
    content_type = models.ForeignKey(to=ContentType, verbose_name="被评论对象的类型")
    object_id = models.CharField(max_length=20, null=False, verbose_name="被评论对象的ID")
    content_object = GenericForeignKey()

    class Meta:
        db_table = "db_article_vote"
        verbose_name = "文章投票"
        verbose_name_plural = verbose_name
        unique_together = ("user_id", "content_type", "object_id")  # 禁止重复投票
