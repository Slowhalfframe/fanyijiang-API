from datetime import datetime

from django.db.models import Q
from django.db import transaction

from apps.utils.api import CustomAPIView
from .serializers import QuestionCreateSerializer, NewQuestionSerializer, AnswerCreateSerializer, \
    QuestionFollowSerializer, FollowedQuestionSerializer, InviteCreateSerializer, QACommentCreateSerializer, \
    QACommentDetailSerializer
from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment, ACVote

from apps.notifications.views import notification_handler

from apps.taskapp.tasks import answers_pv_record


class QuestionView(CustomAPIView):
    def post(self, request):
        """提问"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_asks = "小学生"  # TODO 虚假的名称

        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", ""),
            "labels": request.data.getlist("labels", []),
            "user_id": user_id
        }
        s = QuestionCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)

        instance.who_asks = who_asks
        s = NewQuestionSerializer(instance=instance)
        return self.success(s.data)


class QuestionDetailView(CustomAPIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist as e:
            return self.error(e.args, 401)
        answer_ids = [i.pk for i in question.answer_set.all()]  # TODO 返回哪些答案
        data = {
            "pk": question.pk,
            "answer_numbers": question.answer_set.count(),
            "answer_ids": answer_ids,
            "title": question.title,
            "content": question.content,
            "user_id": question.user_id,  # 提问者ID
            "who_asks": "小学生",  # TODO 提问者称呼
            "when": question.create_at.strftime(format="%Y%m%d %H:%M:%S"),
            "labels": [name[0] for name in question.labels.values_list("name")],
            "follow_numbers": question.questionfollow_set.count(),
            "comment_numbers": question.comment.count(),
            # TODO 阅读量、问题的评论等其他信息
        }
        return self.success(data)


class QuestionCommentView(CustomAPIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist as e:
            return self.error(e.args, 401)
        comments = question.comment.all()
        s = QACommentDetailSerializer(instance=comments, many=True)
        return self.success(s.data)


class AnswerDetailView(CustomAPIView):
    def get(self, request, answer_id):
        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist as e:
            return self.error(e.args, 401)
        data = {
            "pk": answer.pk,
            "votes": answer.vote.filter(value=True).count() - answer.vote.filter(value=False).count(),
            "user_id": answer.user_id,
            "avatar": "avatars/001.jpg",  # TODO 头像URL
            "nickname": "euler",  # TODO 昵称
            "content": answer.content,
            "when": answer.create_at.strftime(format="%Y%m%d %H:%M:%S"),
            # TODO 回答的评论等信息
        }

        # TODO 记录阅读量
        answers_pv_record.delay(request.META.get('REMOTE_ADDR'), answer.id)
        return self.success(data)


class AnswerView(CustomAPIView):
    def post(self, request, question_id):
        """回答问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "45c48cce2e2d7fbdea1afc51c7c6ad26"  # TODO 虚假的ID
        who_answers = "大师"  # TODO 虚假的名称

        data = {
            "question": question_id,
            "content": request.data.get("content", None),
            "user_id": user_id,
        }
        s = AnswerCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            with transaction.atomic():
                instance = s.create(s.validated_data)
                # 保存回答后，把该用户收到的该问题的未回答邀请都设置为已回答
                QuestionInvite.objects.filter(question=question_id, invited=user_id, status=0).update(status=2)
        except Exception as e:
            return self.error(e.args, 401)

        data = dict(AnswerCreateSerializer(instance=instance).data)
        data.pop("user_id")
        data["who_answers"] = who_answers

        # TODO 触发消息通知
        try:
            print('触发消息通知')
            question = Question.objects.get(pk=question_id)
            notification_handler(user_id, question.user_id, 'A', instance)
        except Question.DoesNotExist as e:
            return self.error(e.args, 404)
        return self.success(data)

    def put(self, request, question_id):
        """修改回答，只能修改本人的回答"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_answers = "大师"  # TODO 虚假的名称

        content = request.data.get("content", None)
        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.content = content
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)

        data = dict(AnswerCreateSerializer(instance=instance).data)
        data.pop("user_id")
        data["who_answers"] = who_answers
        return self.success(data)

    def delete(self, request, question_id):
        """删除回答，只能删除本人的回答"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()


class QuestionFollowView(CustomAPIView):
    def post(self, request):
        """关注问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "question": request.data.get("question", None)
        }
        s = QuestionFollowSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def delete(self, request):
        """取消关注问题"""

        user = request.user  # TODO 检查用户权限，只能取消自己关注的问题
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        question = request.data.get("question", None)
        try:
            QuestionFollow.objects.get(question=question, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request):
        """查看本人关注的问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        follows = QuestionFollow.objects.filter(user_id=user_id)
        questions = [i.question for i in follows]
        s = FollowedQuestionSerializer(instance=questions, many=True)
        return self.success(s.data)


class InvitationView(CustomAPIView):
    def post(self, request):
        """邀请回答，不能邀请自己、已回答用户，不能重复邀请同一用户回答同一问题"""

        user = request.user  # TODO 检查用户权限
        user_id = "a87ff679a2f3e71d9181a67b7542122c"  # TODO 虚假的ID

        data = {
            "question": request.data.get("question", None),
            "inviting": user_id,
            "invited": request.data.get("invited", None)  # TODO 被邀请者，暂时采用ID
        }
        s = InviteCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        s.validated_data["status"] = 0  # 未回答
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = InviteCreateSerializer(instance=instance)

        # TODO 发送消息通知
        question = Question.objects.filter(pk=data.get('question')).first()
        notification_handler(instance.inviting, instance.invited, 'I', question)
        return self.success(s.data)

    def delete(self, request):
        """撤销邀请，只能撤销本人发出的未回答的邀请"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "question": request.data.get("question", None),
            "inviting": user_id,
            "invited": request.data.get("invited", None),  # TODO 被邀请者，暂时采用ID
            "status": 0  # 未回答
        }
        try:
            QuestionInvite.objects.get(**data).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def put(self, request):
        """拒绝收到的未回答的邀请"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "pk": request.data.get("invitation", None),
            "invited": user_id,  # 用户需要是被邀请者
            "status": 0,  # 未回答
        }
        try:
            instance = QuestionInvite.objects.get(**data)
            instance.status = 1  # 已拒绝
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request):
        """查询用户发出和收到的邀请"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            query_set = QuestionInvite.objects.filter(Q(invited=user_id) | Q(inviting=user_id))  # TODO 进一步，过滤哪些状态？
        except Exception as e:
            return self.error(e.args, 401)
        s = InviteCreateSerializer(instance=query_set, many=True)
        return self.success(s.data)


class CommentView(CustomAPIView):
    def post(self, request):
        """对问题或回答发表评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        which_model = Question if request.data.get("type", "") == "question" else Answer
        instance_pk = request.data.get("id", None)
        try:
            which_object = which_model.objects.get(pk=instance_pk)  # 被评论的问题或回答对象
        except which_model.DoesNotExist as e:
            return self.error(e.args, 401)
        data = {
            "user_id": user_id,  # 评论者ID
            "content": request.data.get("content", None),  # 评论内容
            "reply_to_user": which_object.user_id,  # 被评论者ID
            "content_object": which_object,
        }
        s = QACommentCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        # TODO s.validated_data里没有content_object，所以自行组织数据了，有什么方法解决？
        data = {
            "user_id": s.validated_data["user_id"],
            "content": s.validated_data["content"],
            "reply_to_user": s.validated_data["reply_to_user"],
            "content_object": which_object,
        }
        try:
            comment = QAComment(**data)
            comment.save()

            # 可通过这种方式创建~
            # data = {
            #     "user_id": s.validated_data["user_id"],
            #     "content": s.validated_data["content"],
            #     "reply_to_user": s.validated_data["reply_to_user"],
            # }
            #
            # comment = which_object.comment.create(**data)  GenericRelation会自动关联
        except Exception as e:
            return self.error(e.args, 401)
        s = QACommentCreateSerializer(instance=comment)

        # TODO 触发消息通知
        if request.data.get("type", "") == "question":
            notification_handler(user_id, which_object.user_id, 'CQ', which_object)
        else:
            notification_handler(user_id, which_object.user_id, 'CAN', which_object)
        return self.success(s.data)

    def delete(self, request):
        """撤销本人发表的问答评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        pk = request.data.get("pk", None)
        try:
            QAComment.objects.get(pk=pk, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def patch(self, request):
        """修改本人发表的问答评论"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        pk = request.data.get("pk", None)
        content = request.data.get("content", None)
        try:
            comment = QAComment.objects.get(pk=pk, user_id=user_id)
            comment.content = content
            comment.save()
        except Exception as e:
            return self.error(e.args, 401)
        s = QACommentCreateSerializer(instance=comment)
        return self.success(s.data)


class VoteView(CustomAPIView):
    def post(self, request):
        """对回答、问答评论进行投票"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        which_model = Answer if request.data.get("type", "") == "answer" else QAComment
        instance_pk = request.data.get("id", None)
        try:
            which_object = which_model.objects.get(pk=instance_pk)  # 被投票的对象，可以是回答或者问答评论
            # TODO 能否给自己投票？
        except which_model.DoesNotExist as e:
            return self.error(e.args, 401)
        value = request.data.get("value", None)
        value = bool(value)  # TODO 具体哪些值看作True，哪些看作False?
        data = {
            "user_id": user_id,  # 投票者ID
            "value": value,
            "content_object": which_object
        }

        try:
            vote = ACVote(**data)
            vote.save()
        except Exception as e:
            return self.error(e.args, 401)
        data = {
            "user_id": vote.user_id,
            "value": vote.value,
            "ac_id": vote.object_id,
            "pk": vote.pk,
        }
        # TODO 触发消息通知
        if request.data.get("type", "") == "answer" and value == True:
            notification_handler(user_id, which_object.user_id, 'LAN', which_object)

        return self.success(data)

    def delete(self, request):
        """撤销投票"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        pk = request.data.get("pk", None)
        try:
            ACVote.objects.get(pk=pk, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()
