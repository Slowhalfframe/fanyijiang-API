from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.

class ReadNums(models.Model):
    nums = models.IntegerField(default=0, verbose_name='总阅读量')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100, verbose_name='对象ID')
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'db_read_nums'
        verbose_name = '阅读量'
        verbose_name_plural = verbose_name
