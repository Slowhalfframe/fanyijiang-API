from django.db import models


class Label(models.Model):
    """问题、文章等的标签"""
    name = models.CharField(max_length=20, unique=True, null=False, verbose_name="标签名称")  # 无重复标签
    intro = models.TextField(null=False, verbose_name="标签介绍")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    children = models.ManyToManyField(to="self", symmetrical=False, verbose_name="子标签",blank=True)

    class Meta:
        db_table = "db_labels"
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class LabelFollow(models.Model):
    """标签关注"""
    user_id = models.CharField(max_length=40, null=False, verbose_name="关注者ID")
    label = models.ForeignKey(to=Label, null=False, verbose_name="关注的标签")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        db_table = "db_label_follows"
        verbose_name = "标签关注"
        verbose_name_plural = verbose_name
        unique_together = (("user_id", "label"),)  # 无重复关注
