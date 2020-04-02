import random

from django.db.models import Q
from django.db import transaction

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.utils import errorcode
from .serializers import QuestionCreateSerializer, NewQuestionSerializer, AnswerCreateSerializer, \
    QuestionFollowSerializer, FollowedQuestionSerializer, InviteCreateSerializer, QACommentCreateSerializer, \
    QACommentDetailSerializer, TwoAnswersSerializer, AnswerWithAuthorInfoSerializer
from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment
from apps.userpage.models import UserProfile

from apps.taskapp.tasks import notification_handler

from apps.taskapp.tasks import answers_pv_record, question_pv_record


class QuestionView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """提问"""

        user_id = request._request.uid  # TODO 提问的权限
        labels = request.data.getlist("labels", [])
        if len(labels) == 1:
            labels = labels[0].split(",")
        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", ""),
            "labels": labels,
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
        question = Question.objects.filter(pk=question_id).first()
        if not question:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
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
        question = Question.objects.filter(pk=question_id).first()
        if not question:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        comments = question.comment.all()
        me = self.get_user_profile(request)
        data = self.paginate_data(request, query_set=comments, object_serializer=QACommentDetailSerializer,
                                  serializer_context={"me": me})
        return self.success(data)


class AnswerDetailView(CustomAPIView):
    def get(self, request, question_id, answer_id):
        question = Question.objects.filter(pk=question_id).first()
        answer = Answer.objects.filter(pk=answer_id, question_id=question_id).first()
        if not question or not answer:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
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


class AnswerCommentView(CustomAPIView):
    def get(self, request, question_id, answer_id):
        """获取回答的所有评论"""

        question = Question.objects.filter(pk=question_id).first()
        answer = Answer.objects.filter(pk=answer_id, question_id=question_id).first()
        if not question or not answer:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        comments = answer.comment.all()
        me = self.get_user_profile(request)
        data = self.paginate_data(request, query_set=comments, object_serializer=QACommentDetailSerializer,
                                  serializer_context={"me": me})
        return self.success(data)


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
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)

        s = AnswerCreateSerializer(instance=instance)

        # TODO 触发消息通知
        try:
            print('触发消息通知')
            question = Question.objects.get(pk=question_id)
            notification_handler.delay(user_id, question.user_id, 'A', instance.id)

            # TODO 是否也要给关注该问题的人发送通知，是否要异步发送
            question_follows = QuestionFollow.objects.filter(question=question)
            for follow in question_follows:
                notification_handler.delay(user_id, follow.user_id, 'AF', instance.id)
        except Question.DoesNotExist as e:
            return self.error(e.args, errorcode.INVALID_DATA)
        return self.success(s.data)

    @validate_identity
    def put(self, request, question_id):
        """修改回答，只能修改本人的回答"""

        user_id = request._request.uid
        content = request.data.get("content", None)
        instance = Answer.objects.filter(question=question_id, user_id=user_id).first()
        if not instance:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            instance.content = content
            instance.save()
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = AnswerCreateSerializer(instance=instance)
        return self.success(s.data)

    @validate_identity
    def delete(self, request, question_id):
        """删除回答，只能删除本人的回答"""

        answer = Answer.objects.filter(question=question_id, user_id=request._request.uid).first()
        if not answer:
            return self.success()
        try:
            answer.delete()
        except:
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
        instance = QuestionFollow.objects.filter(question=question, user_id=request._request.uid).first()
        if not instance:
            return self.success()
        try:
            instance.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def get(self, request):
        """查看本人关注的问题"""

        questions = Question.objects.filter(questionfollow__user_id=request._request.uid).all()
        data = self.paginate_data(request, query_set=questions, object_serializer=FollowedQuestionSerializer)
        return self.success(data)


class InvitationView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """邀请回答，不能邀请自己、已回答用户，不能重复邀请同一用户回答同一问题"""

        slug = request.data.get("invited_slug", None)
        invited = UserProfile.objects.filter(slug=slug).first()
        if not invited:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "question": request.data.get("id", None),
            "inviting": request._request.uid,
            "invited": invited.uid,
        }
        s = InviteCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        s.validated_data["status"] = 0
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)

        # TODO 发送消息通知
        question = Question.objects.filter(pk=data.get('question')).first()
        # notification_handler.delay(instance.inviting, instance.invited, 'I', question.id)
        return self.success()

    @validate_identity
    def delete(self, request):
        """撤销邀请，只能撤销本人发出的未回答的邀请"""

        invited_slug = request.GET.get("invited_slug", None)
        invited = UserProfile.objects.filter(slug=invited_slug).first()
        if not invited:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        data = {
            "question": request.GET.get("id", None),
            "inviting": request._request.uid,
            "invited": invited.uid,
        }
        instance = QuestionInvite.objects.filter(**data).first()
        if not instance:
            return self.success()
        if instance.status != 0:  # 0表示未回答
            return self.error(errorcode.MSG_INVITATION_DONE, errorcode.INVITATION_DONE)
        try:
            instance.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def put(self, request):
        """拒绝收到的未回答的邀请"""

        instance = QuestionInvite.objects.filter(pk=request.data.get("id", None)).first()
        if not instance:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if instance.invited != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        if instance.status != 0:
            return self.error(errorcode.MSG_INVITATION_DONE, errorcode.INVITATION_DONE)
        try:
            instance.status = 1  # 已拒绝
            instance.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def get(self, request):
        """查询用户发出和收到的邀请"""

        user_id = request._request.uid
        query_set = QuestionInvite.objects.filter(Q(invited=user_id) | Q(inviting=user_id))  # TODO 进一步，过滤哪些状态？
        s = InviteCreateSerializer(instance=query_set, many=True)
        return self.success(s.data)


class HelperView(CustomAPIView):
    @validate_identity
    def get(self, request):
        """获取当前用户可邀请的用户，不能邀请已邀请过的用户"""

        user_id = request._request.uid
        question = request.GET.get("question", None)
        invited = QuestionInvite.objects.filter(inviting=user_id, question=question).values("invited")
        helpers = UserProfile.objects.exclude(uid=user_id).exclude(uid__in=invited)  # TODO 主动拒绝邀请的也要排除
        if len(helpers) > 15:  # 用户超过15个时，随机抽取15个
            helpers = random.sample(list(helpers), 15)
        data = [{"nickname": user.nickname, "avatar": user.avatar, "slug": user.slug, "status": False} for user in
                helpers]  # status表示是否已经邀请过
        return self.success(data)


class CommentView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """对问题或回答发表评论"""

        user_id = request._request.uid
        which_model = Question if request.data.get("type", "") == "question" else Answer  # TODO 对评论发表评论
        instance_pk = request.data.get("id", None)
        which_object = which_model.objects.filter(pk=instance_pk).first()
        if not which_object:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
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
            # 评论问题
            notification_handler.delay(user_id, which_object.user_id, 'CQ', comment.id)
        else:
            # 评论回答
            notification_handler.delay(user_id, which_object.user_id, 'CAN', comment.id)
        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """撤销本人发表的问答评论"""

        comment = QAComment.objects.filter(pk=request.GET.get("id", None)).first()
        if not comment:
            return self.success()
        if comment.user_id != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            comment.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def patch(self, request):
        """修改本人发表的问答评论"""

        comment = QAComment.objects.filter(pk=request.data.get("id", None)).first()
        if not comment:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if comment.user_id != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        content = request.data.get("content", None)
        try:
            comment.content = content
            comment.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = QACommentCreateSerializer(instance=comment)
        return self.success(s.data)


class VoteView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """对回答、问答评论进行投票或者修改已有的投票"""

        user_id = request._request.uid
        which_model = Answer if request.data.get("type", "") == "answer" else QAComment
        which_object = which_model.objects.filter(pk=request.data.get("id", None)).first()  # 被投票的对象，可以是回答或者问答评论
        if not which_object:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # TODO 能否给自己投票？
        value = request.data.get("value", "0")
        value = bool(int(value))  # value采用数字
        try:
            which_object.vote.update_or_create(user_id=user_id, defaults={'value': value})
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        # TODO 触发消息通知
        if which_model == Answer and value == True:
            notification_handler.delay(user_id, which_object.user_id, 'LAN', which_object.id)
        elif which_model == QAComment and value == True:
            notification_handler.delay(user_id, which_object.user_id, 'LQAC', which_object.id)
        return self.success()

    @validate_identity
    def delete(self, request):
        """撤销投票"""

        user_id = request._request.uid
        pk = request.GET.get("id", None)  # 回答或评论的ID
        which_model = Answer if request.GET.get("type", "") == "answer" else QAComment
        which_object = which_model.objects.filter(pk=pk).first()  # 此票所属对象
        if not which_object:
            return self.success()
        old_vote = which_object.vote.filter(user_id=user_id).first()  # 要撤销的票
        if not old_vote:
            return self.success()
        try:
            old_vote.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()
