from rest_framework import serializers
from .models import Notification


class NotificationsSerializer(serializers.ModelSerializer):
    # detail = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    verb = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('actor', 'verb', 'target', 'created_at')

    def get_actor(self, obj):
        actor = obj.actor
        data = {
            'nickname': actor.nickname,
            'slug': actor.slug
        }
        return data

    def get_verb(self, obj):
        return obj.get_verb_display()

    def get_target(self, obj):
        action_object = obj.action_object
        verb = obj.verb
        data = {}


        if verb == 'O':
            # 关注了你
            pass

        if verb == 'I':
            # 邀请了你
            data['title'] = action_object.title
            data['id'] = action_object.id
            data['link'] = ''  # 问题详情

        if verb == 'R':
            # 评论了你的问题
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 问题评论详情

        if verb == 'A':
            # 回答了你的问题
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情页

        if verb == 'LA':
            pass

        if verb == 'LAN':
            # 赞了你的问答
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答详情页

        if verb == 'LAR':
            # 赞了你的文章
            data['title'] = action_object.title
            data['id'] = action_object.id
            data['link'] = ''  # 文章详情

        if verb == 'LC':
            # 赞了你的评论
            data['title'] = action_object.content
            data['id'] = action_object.id
            data['link'] = ''  # 评论详情

        if verb == 'CAN':
            # 评论了你的回答
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 回答评论详情

        if verb == 'CAR':
            # 评论了你的文章
            data['title'] = action_object.title
            data['id'] = action_object.id
            data['link'] = ''  # 文章评论详情

        if verb == 'CQ':
            # 评论了你的问题
            data['title'] = action_object.question.title
            data['id'] = action_object.id
            data['link'] = ''  # 问题评论详情
        return data
