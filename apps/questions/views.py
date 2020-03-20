import random

from django.db.models import Q
from django.db import transaction

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.utils import errorcode
from .serializers import QuestionCreateSerializer, NewQuestionSerializer, AnswerCreateSerializer, \
    QuestionFollowSerializer, FollowedQuestionSerializer, InviteCreateSerializer, QACommentCreateSerializer, \
    QACommentDetailSerializer, TwoAnswersSerializer, AnswerWithAuthorInfoSerializer
from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment, ACVote
from apps.userpage.models import UserProfile

from apps.notifications.views import notification_handler

from apps.taskapp.tasks import answers_pv_record, question_pv_record


class QuestionView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """提问"""

        user_id = request._request.uid  # TODO 提问的权限
        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", ""),
            "labels": request.data.getlist("labels", []),
            "user_id": user_id
        }
        s = QuestionCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = NewQuestionSerializer(instance=instance)
        return self.success(s.data)


class QuestionDetailView(CustomAPIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        user = UserProfile.objects.get(uid=question.user_id)  # TODO 用户不存在怎么处理？
        me = self.get_user_profile(request)
        if not me:
            followed = False
            answered = False
        else:
            followed = question.questionfollow_set.filter(user_id=me.uid).exists()
            answered = question.answer_set.filter(user_id=me.uid).first()
            answered = False if not answered else answered.id
        data = {
            "id": question.pk,
            "answer_numbers": question.answer_set.count(),
            "answered": answered,  # 当前登录用户未回答时为False，否则为回答的ID
            "answers": self.paginate_data(request, query_set=question.answer_set.all(),
                                          object_serializer=AnswerWithAuthorInfoSerializer,
                                          serializer_context={"me": me}),
            "title": question.title,
            "content": question.content,
            "author_info": {
                "nickname": user.nickname,
                "avatar": user.avatar,
                "slug": user.slug,
            },
            "create_at": question.create_at.strftime(format="%Y%m%d %H:%M:%S"),
            "labels": [{"id": i.id, "name": i.name} for i in question.labels.all()],
            "follow_numbers": question.questionfollow_set.count(),
            "comment_numbers": question.comment.count(),
            "followed": followed,
            # TODO 阅读量、问题的评论等其他信息
        }

        # TODO 记录阅读量
        question_pv_record.delay(request.META.get('REMOTE_ADDR'), question.id)
        return self.success(data)


class QuestionCommentView(CustomAPIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        comments = question.comment.all()
        data = self.paginate_data(request, query_set=comments, object_serializer=QACommentDetailSerializer)
        return self.success(data)


class AnswerDetailView(CustomAPIView):
    def get(self, request, question_id, answer_id):
        try:
            question = Question.objects.get(pk=question_id)
            answer = Answer.objects.get(pk=answer_id, question_id=question_id)
        except (Question.DoesNotExist, Answer.DoesNotExist):
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        another_answer = question.answer_set.exclude(pk=answer_id)
        if another_answer.exists():
            another_answer = random.choice(another_answer)
        else:
            another_answer = None
        me = self.get_user_profile(request)
        answer.me = me  # me不便通过context传递给AnswerWithAuthorInfoSerializer
        if another_answer:
            another_answer.me = me
        s = TwoAnswersSerializer(instance={"answer": answer, "another_answer": another_answer}, context={"me": me})
        # TODO 记录阅读量
        answers_pv_record.delay(request.META.get('REMOTE_ADDR'), answer.id)
        return self.success(s.data)


class AnswerView(CustomAPIView):
    @validate_identity
    def post(self, request, question_id):
        """回答问题"""

        user_id = request._request.uid
        data = {
            "question": question_id,
            "content": request.data.get("content", None),
            "user_id": user_id,
        }
        s = AnswerCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            with transaction.atomic():
                instance = s.create(s.validated_data)
                # 保存回答后，把该用户收到的该问题的未回答邀请都设置为已回答
                QuestionInvite.objects.filter(question=question_id, invited=user_id, status=0).update(status=2)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)

        s = AnswerCreateSerializer(instance=instance)
        # TODO 触发消息通知
        try:
            print('触发消息通知')
            question = Question.objects.get(pk=question_id)
            notification_handler(user_id, question.user_id, 'A', instance)
        except Question.DoesNotExist as e:
            return self.error(e.args, errorcode.INVALID_DATA)
        return self.success(s.data)

    @validate_identity
    def put(self, request, question_id):
        """修改回答，只能修改本人的回答"""

        user_id = request._request.uid
        content = request.data.get("content", None)
        try:
            instance = Answer.objects.get(question=question_id, user_id=user_id)
            instance.content = content
            instance.save()
        except Answer.DoesNotExist:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)

        s = AnswerCreateSerializer(instance=instance)
        return self.success(s.data)

    @validate_identity
    def delete(self, request, question_id):
        """删除回答，只能删除本人的回答"""

        try:
            Answer.objects.get(question=question_id, user_id=request._request.uid).delete()
        except Answer.DoesNotExist:
            pass
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class QuestionFollowView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """关注问题"""

        data = {
            "user_id": request._request.uid,
            "question": request.data.get("id", None)
        }
        s = QuestionFollowSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def delete(self, request):
        """取消关注问题"""

        question = request.GET.get("id", None)
        try:
            QuestionFollow.objects.get(question=question, user_id=request._request.uid).delete()
        except QuestionFollow.DoesNotExist:
            pass
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
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

        invited_slug = request.data.get("invited_slug", None)
        try:
            invited = UserProfile.objects.get(slug=invited_slug).uid
        except:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "question": request.data.get("id", None),
            "inviting": request._request.uid,
            "invited": invited
        }
        s = InviteCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        s.validated_data["status"] = 0  # 未回答
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = InviteCreateSerializer(instance=instance)

        # TODO 发送消息通知
        question = Question.objects.filter(pk=data.get('question')).first()
        notification_handler(instance.inviting, instance.invited, 'I', question)
        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """撤销邀请，只能撤销本人发出的未回答的邀请"""

        invited_slug = request.GET.get("invited_slug", None)
        try:
            invited = UserProfile.objects.get(slug=invited_slug)
        except UserProfile.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "question": request.GET.get("id", None),
            "inviting": request._request.uid,
            "invited": invited.uid,
            "status": 0  # 未回答
        }
        try:
            QuestionInvite.objects.get(**data).delete()
        except QuestionInvite.DoesNotExist:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def put(self, request):
        """拒绝收到的未回答的邀请"""

        data = {
            "pk": request.data.get("id", None),
            "invited": request._request.uid,  # 用户需要是被邀请者
            "status": 0,  # 未回答
        }
        try:
            instance = QuestionInvite.objects.get(**data)
            instance.status = 1  # 已拒绝
            instance.save()
        except QuestionInvite.DoesNotExist:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def get(self, request):
        """查询用户发出和收到的邀请"""

        user_id = request._request.uid
        try:
            query_set = QuestionInvite.objects.filter(Q(invited=user_id) | Q(inviting=user_id))  # TODO 进一步，过滤哪些状态？
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = InviteCreateSerializer(instance=query_set, many=True)
        return self.success(s.data)


class HelperView(CustomAPIView):
    @validate_identity
    def get(self, request):
        """获取当前用户可邀请的用户，不能邀请已邀请过的用户"""

        user_id = request._request.uid
        invited = QuestionInvite.objects.filter(inviting=user_id).values("invited")
        helpers = UserProfile.objects.exclude(uid=user_id).exclude(uid__in=invited)  # TODO 主动拒绝邀请的也要排除
        if len(helpers) > 15:  # 用户超过15个时，随机抽取15个
            helpers = random.sample(list(helpers), 15)
        data = [{"nickname": user.nickname, "avatar": user.avatar, "slug": user.slug} for user in helpers]
        return self.success(data)


class CommentView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """对问题或回答发表评论"""

        user_id = request._request.uid
        which_model = Question if request.data.get("type", "") == "question" else Answer
        instance_pk = request.data.get("id", None)
        try:
            which_object = which_model.objects.get(pk=instance_pk)  # 被评论的问题或回答对象
        except which_model.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "user_id": user_id,  # 评论者ID
            "content": request.data.get("content", None),  # 评论内容
            "reply_to_user": which_object.user_id,  # 被评论者ID
            "content_object": which_object,
        }
        s = QACommentCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "user_id": s.validated_data["user_id"],
            "content": s.validated_data["content"],
            "reply_to_user": s.validated_data["reply_to_user"],
        }
        try:
            comment = which_object.comment.create(**data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
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
            QAComment.objects.get(pk=request.GET.get("id", None), user_id=request._request.uid).delete()
        except QAComment.DoesNotExist:
            pass
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def patch(self, request):
        """修改本人发表的问答评论"""

        pk = request.data.get("id", None)
        content = request.data.get("content", None)
        try:
            comment = QAComment.objects.get(pk=pk, user_id=request._request.uid)
            comment.content = content
            comment.save()
        except QAComment.DoesNotExist:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
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
        except which_model.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
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
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        # TODO 触发消息通知
        if request.data.get("type", "") == "answer" and value == True:
            notification_handler(user_id, which_object.user_id, 'LAN', which_object)

        return self.success()

    @validate_identity
    def delete(self, request):
        """撤销投票"""

        pk = request.GET.get("id", None)
        user_id = request._request.uid
        try:
            ACVote.objects.get(pk=pk, user_id=user_id).delete()
        except ACVote.DoesNotExist:
            pass
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()
