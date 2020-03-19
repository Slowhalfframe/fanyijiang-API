from django.shortcuts import render

from apps.utils.api import CustomAPIView
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationsSerializer

from apps.userpage.models import UserProfile
from apps.utils.decorators import validate_identity


def notification_handler(actor_uid, recipient_uid, verb, action_object, **kwargs):
    """
    通知处理器
    :param actor_uid:           触发者对象id
    :param recipient_uid:       接受者对象id，可以是一个或者多个接收者
    :param verb:                str 通知类别
    :param action_object:       Instance 动作对象的实例
    :return:                    None
    """
    NOTIFICATION_TYPE = (
        ('LAN', '赞了你的回答'),  # like answer
        ('LAR', '赞了你的文章'),  # like article
        ('LC', '赞了你的评论'),  # like comment
        ('CAN', '评论了你的回答'),  # comment answer
        ('CAR', '评论了你的文章'),  # comment article
        ('CQ', '评论了你的问题'),  # comment question
        ('R', '回复了你'),  # reply
        ('FAN', '收藏了你的回答'),  # favor answer
        ('FAR', '收藏了你的文章'),  # favor article
        ('A', '回答了你的问题'),  # answer
        ('I', '的提问等你来答'),  # invited
        ('O', '关注了你'),  # follow
    )

    if verb == 'I':
        # 传入问题对象
        is_object = actor_uid == action_object.user_id
    elif verb == 'A':
        # 传入回答对象
        is_object = recipient_uid == action_object.question.user_id
    elif verb == 'O':
        # 传入用户对象
        is_object = recipient_uid == action_object.uid
    elif verb == 'CAN':
        # 传入评论对象
        is_object = recipient_uid == action_object.answer.user_id
    elif verb == 'CAR':
        # 传入评论对象
        is_object = recipient_uid == action_object.article.user_id
    # elif verb == 'CQ':
    #     # 传入评论对象
    #     is_object = recipient_uid == action_object.user_id
    else:
        is_object = recipient_uid == action_object.user_id

    is_actor = actor_uid != recipient_uid

    if is_actor and is_object:
        # 只通知接收者，即recipient == 动作对象的作者
        # 记录通知内容
        actor = UserProfile.objects.get(uid=actor_uid)
        recipient = UserProfile.objects.get(uid=recipient_uid)
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )


class NotificationAPIView(CustomAPIView):
    '''获取所有通知'''
    @validate_identity
    def get(self, request):
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        nos = Notification.objects.filter(recipient__uid=uid)
        # 在获取的时候就已经把所有未读的变成已读
        Notification.objects.filter(recipient__uid=uid, unread=True).update(unread=False)
        # data = NotificationsSerializer(nos, many=True).data
        data = self.paginate_data(request, nos, NotificationsSerializer)
        return self.success(data)