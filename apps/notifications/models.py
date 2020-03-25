from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from apps.userpage.models import UserProfile


# Create your models here.
class Notification(models.Model):
    NOTIFICATION_TYPE = (
        ('LAN', '赞了你的回答'),  # like answer
        ('LAR', '赞了你的文章'),  # like article
        ('LI', '赞了你的文章'),  # like article
        ('LQAC', '赞了你的评论'),  # like comment回答的评论
        ('LAC', '赞了你的评论'),  # like comment文章的评论
        ('LIC', '赞了你的评论'),  # like comment想法的评论
        # ('LQC', '赞了你的评论'),  # like comment问题的评论
        # ('LRC', '赞了你的评论'),  # like comment文章的评论
        # ('LTC', '赞了你的评论'),  # like comment想法的评论
        ('CAN', '评论了你的回答'),  # comment answer
        ('CAR', '评论了你的文章'),  # comment article
        ('CQ', '评论了你的问题'),  # comment question
        ('CI', '评论了你的想法'),  # comment idea
        ('R', '回复了你'),  # reply
        ('A', '回答了你的问题'),  # answer
        ('AF', '回答了你关注的问题'),  # answer
        ('I', '的提问等你来答'),  # invited
        ('O', '关注了你'),  # follow
    )
    actor = models.ForeignKey(UserProfile, related_name="notify_actor",
                              on_delete=models.CASCADE, verbose_name="触发者")
    recipient = models.ForeignKey(UserProfile, null=True, blank=False,
                                  related_name="notifications", on_delete=models.CASCADE, verbose_name='接收者')
    unread = models.BooleanField(default=True, verbose_name='未读')
    verb = models.CharField(max_length=4, choices=NOTIFICATION_TYPE, verbose_name="通知类别")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    content_type = models.ForeignKey(ContentType, related_name='notify_action_object', null=True, blank=True,
                                     on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    action_object = GenericForeignKey()  # 或GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = 'db_notifications'
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)
