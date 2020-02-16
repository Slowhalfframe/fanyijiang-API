from django.db import models


class Label(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="标签名称")
    intro = models.TextField(null=False, blank=False, verbose_name="标签介绍")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "db_labels"
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class LabelRelation(models.Model):
    """标签的多对多层次关系。"""
    parent = models.ForeignKey(to=Label, on_delete=models.CASCADE, related_name="as_parent", verbose_name="父标签")
    child = models.ForeignKey(to=Label, on_delete=models.CASCADE, related_name="as_child", verbose_name="子标签")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "db_labels_rels"
        verbose_name = "标签关系"
        verbose_name_plural = "标签关系"

    def __str__(self):
        return "{}:{}".format(self.parent, self.child)
