from django.db.models import Q
from django.db import transaction

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from .serializers import QuestionCreateSerializer, NewQuestionSerializer, AnswerCreateSerializer, \
    QuestionFollowSerializer, FollowedQuestionSerializer, InviteCreateSerializer, QACommentCreateSerializer, \
    QACommentDetailSerializer
from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment, ACVote
from apps.userpage.models import UserProfile

from apps.notifications.views import notification_handler

from apps.taskapp.tasks import answers_pv_record


class QuestionView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """提问"""

        user_id = request._request.uid  # TODO 提问的权限
        user = UserProfile.objects.get(uid=user_id)
        who_asks = user.nickname
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
        user = UserProfile.objects.get(uid=question.user_id)  # TODO 用户不存在怎么处理？
        who_asks = user.nickname
        data = {
            "pk": question.pk,
            "answer_numbers": question.answer_set.count(),
            "answer_ids": answer_ids,
            "title": question.title,
            "content": question.content,
            "user_id": question.user_id,
            "who_asks": who_asks,
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
        user = UserProfile.objects.get(uid=answer.user_id)  # TODO 用户不存在怎么办？
        data = {
            "pk": answer.pk,
            "votes": answer.vote.filter(value=True).count() - answer.vote.filter(value=False).count(),
            "user_id": answer.user_id,
            "avatar": user.avatar,
            "nickname": user.nickname,
            "content": answer.content,
            "when": answer.create_at.strftime(format="%Y%m%d %H:%M:%S"),
            # TODO 回答的评论等信息
        }

        # TODO 记录阅读量
        answers_pv_record.delay(request.META.get('REMOTE_ADDR'), answer.id)
        return self.success(data)


class AnswerView(CustomAPIView):
    @validate_identity
    def post(self, request, question_id):
        """回答问题"""

        user_id = request._request.uid
        user = UserProfile.objects.get(uid=user_id)
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
        data["who_answers"] = user.nickname

        # TODO 触发消息通知
        try:
            print('触发消息通知')
            question = Question.objects.get(pk=question_id)
            notification_handler(user_id, question.user_id, 'A', instance)
        except Question.DoesNotExist as e:
            return self.error(e.args, 404)
        return self.success(data)

    @validate_identity
    def put(self, request, question_id):
        """修改回答，只能修改本人的回答"""

        user_id = request._request.uid
        user = UserProfile.objects.get(uid=user_id)
        content = request.data.get("content", None)
        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.content = content
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)

        data = dict(AnswerCreateSerializer(instance=instance).data)
        data.pop("user_id")
        data["who_answers"] = user.nickname
        return self.success(data)

    @validate_identity
    def delete(self, request, question_id):
        """删除回答，只能删除本人的回答"""

        try:
            Answer.objects.get(question=question_id, user_id=request._request.uid).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()


class QuestionFollowView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """关注问题"""

        data = {
            "user_id": request._request.uid,
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

    @validate_identity
    def delete(self, request):
        """取消关注问题"""

        question = request.data.get("question", None)
        try:
            QuestionFollow.objects.get(question=question, user_id=request._request.uid).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def get(self, request):
        """查看本人关注的问题"""

        follows = QuestionFollow.objects.filter(user_id=request._request.uid)
        questions = [i.question for i in follows]
        s = FollowedQuestionSerializer(instance=questions, many=True)
        return self.success(s.data)


class InvitationView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """邀请回答，不能邀请自己、已回答用户，不能重复邀请同一用户回答同一问题"""

        data = {
            "question": request.data.get("question", None),
            "inviting": request._request.uid,
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

    @validate_identity
    def delete(self, request):
        """撤销邀请，只能撤销本人发出的未回答的邀请"""

        data = {
            "question": request.data.get("question", None),
            "inviting": request._request.uid,
            "invited": request.data.get("invited", None),  # TODO 被邀请者，暂时采用ID
            "status": 0  # 未回答
        }
        try:
            QuestionInvite.objects.get(**data).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def put(self, request):
        """拒绝收到的未回答的邀请"""

        data = {
            "pk": request.data.get("invitation", None),
            "invited": request._request.uid,  # 用户需要是被邀请者
            "status": 0,  # 未回答
        }
        try:
            instance = QuestionInvite.objects.get(**data)
            instance.status = 1  # 已拒绝
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def get(self, request):
        """查询用户发出和收到的邀请"""

        user_id = request._request.uid
        try:
            query_set = QuestionInvite.objects.filter(Q(invited=user_id) | Q(inviting=user_id))  # TODO 进一步，过滤哪些状态？
        except Exception as e:
            return self.error(e.args, 401)
        s = InviteCreateSerializer(instance=query_set, many=True)
        return self.success(s.data)


class CommentView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """对问题或回答发表评论"""

        user_id = request._request.uid
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
        data = {
            "user_id": s.validated_data["user_id"],
            "content": s.validated_data["content"],
            "reply_to_user": s.validated_data["reply_to_user"],
        }
        try:
            comment = which_object.comment.create(**data)
        except Exception as e:
            return self.error(e.args, 401)
        s = QACommentCreateSerializer(instance=comment)

        # TODO 触发消息通知
        if request.data.get("type", "") == "question":
            notification_handler(user_id, which_object.user_id, 'CQ', which_object)
        else:
            notification_handler(user_id, which_object.user_id, 'CAN', which_object)
        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """撤销本人发表的问答评论"""

        try:
            QAComment.objects.get(pk=request.data.get("pk", None), user_id=request._request.uid).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def patch(self, request):
        """修改本人发表的问答评论"""

        pk = request.data.get("pk", None)
        content = request.data.get("content", None)
        try:
            comment = QAComment.objects.get(pk=pk, user_id=request._request.uid)
            comment.content = content
            comment.save()
        except Exception as e:
            return self.error(e.args, 401)
        s = QACommentCreateSerializer(instance=comment)
        return self.success(s.data)


class VoteView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """对回答、问答评论进行投票"""

        user_id = request._request.uid
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

    @validate_identity
    def delete(self, request):
        """撤销投票"""

        pk = request.data.get("pk", None)
        user_id = request._request.uid
        try:
            ACVote.objects.get(pk=pk, user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()
