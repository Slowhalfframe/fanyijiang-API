from django.db import models


class BaseModel(models.Model):
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_deleted = models.BooleanField(null=False, default=False, verbose_name="逻辑删除")

    class Meta:
        abstract = True
