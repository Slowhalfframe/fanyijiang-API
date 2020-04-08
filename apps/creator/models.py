from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class CreatorList(models.Model):
    object_id = models.IntegerField()
    content_type = models.CharField(max_length=10, verbose_name='内容类型')
    score = models.IntegerField(default=0)
    several_issues = models.ForeignKey('SeveralIssues', on_delete=models.CASCADE, related_name='creator_list')

    class Meta:
        db_table = 'db_creator_list'


class SeveralIssues(models.Model):
    sort = models.IntegerField(default=1, verbose_name='第几期')
    title = models.CharField(max_length=100, verbose_name='名称')
    image = models.CharField(max_length=150, verbose_name='图片路径', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='统计日期')

    class Meta:
        db_table = 'db_several_issues'
