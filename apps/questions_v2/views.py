import random

from django.db.transaction import atomic

from apps.comments.serializers import BasicUserSerializer
from apps.labels_v2.models import Label
from apps.userpage.models import UserProfile
from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in
from .models import Question, Answer, QuestionFollow, QuestionInvite
from .serializers import QuestionChecker, MeQuestionSerializer, AnswerChecker, BasicAnswerSerializer, MeAnswerSerializer


class QuestionView(CustomAPIView):
    @logged_in
    def post(self, request):
        """提问"""

        me = request.me
        # TODO 检查用户权限
        data = {
            "title": request.data.get("title") or "",
            "content": request.data.get("content") or "",
        }
        labels = request.data.getlist("labels") or []
        qs = Label.objects.filter(id__in=labels, is_deleted=False)
        if not qs.exists():
            return self.error(errorcode.MSG_NO_LABELS, errorcode.NO_LABELS)
        checker = QuestionChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            with atomic():
                question = Question.objects.create(author=me, **checker.validated_data)
                question.labels.add(*(i for i in qs))  # question.labels.add(qs)为何出错？
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeQuestionSerializer(instance=question, context={"me": me})
        return self.success(formatter.data)


class OneQuestionView(CustomAPIView):
    # TODO 哪些问题可以删除？
    @logged_in
    def put(self, request, question_id):
        """修改自己的问题"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if question.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        labels = request.data.getlist("labels") or []
        qs = Label.objects.filter(id__in=labels, is_deleted=False)
        if not qs.exists():
            return self.error(errorcode.MSG_NO_LABELS, errorcode.NO_LABELS)
        # TODO 问题的标题不能随意修改，免得造成答非所问
        title = request.data.get("title") or ""
        data = {
            "content": request.data.get("content") or "",
            "title": "a" if question.title == title else title  # 使用无意义但有效的标题，绕过唯一性验证
        }
        checker = QuestionChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        if not question.title == title:
            question.title = checker.validated_data["title"]
        question.content = checker.validated_data["content"]
        try:
            with atomic():
                question.save()
                question.labels.clear()
                question.labels.add(*(i for i in qs))
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeQuestionSerializer(instance=question, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, question_id):
        """查看问题的详情，以及一批回答，可分页"""

        me = self.get_user_profile(request)
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        formatter = MeQuestionSerializer(instance=question, context={"me": me})
        # TODO 返回一批回答
        return self.success(formatter.data)


class AnswerView(CustomAPIView):
    @logged_in
    def post(self, request, question_id):
        """写回答，可以是草稿，正式回答会真实删除草稿"""

        me = request.me
        # TODO 检查用户权限
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # TODO 现在允许自问自答，并且有相关的单元测试，是否修改？
        if question.answer_set.filter(author=me, is_draft=False, is_deleted=False).exists():
            return self.error(errorcode.MSG_ANSWERED, errorcode.ANSWERED)
        data = {
            "content": request.data.get("content") or "",
            "is_draft": request.data.get("is_draft"),
        }
        checker = AnswerChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            with atomic():
                answer = Answer.objects.create(author=me, question=question, **checker.validated_data)
                if answer.is_draft is False:
                    # TODO 可以异步或定时进行
                    question.answer_set.filter(author=me, is_draft=True).delete()
                    # TODO 把本人收到的此问题的尚未回答的回答邀请全部设为已回答
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeAnswerSerializer(instance=answer, context={"me": me})
        return self.success(formatter.data)


class OneAnswerView(CustomAPIView):
    @logged_in
    def delete(self, request, question_id, answer_id):
        """撤销本人的回答，草稿会真实删除，正式回答不能随意删除"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        answer = Answer.objects.filter(pk=answer_id, question=question_id, is_deleted=False).first()
        if question is None or answer is None:
            return self.success()
        if answer.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            if answer.is_draft:
                answer.delete()
            else:  # TODO 哪些正式回答不能删除？
                answer.is_deleted = True
                answer.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def put(self, request, question_id, answer_id):
        """修改本人的回答，不能把正式回答变为草稿，发表正式回答会真实删除草稿"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        answer = Answer.objects.filter(pk=answer_id, question=question_id, is_deleted=False).first()
        if question is None or answer is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if answer.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        data = {
            "content": request.data.get("content") or "",
            "is_draft": request.data.get("is_draft"),
        }
        checker = AnswerChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            answer.content = checker.validated_data["content"]
            if answer.is_draft:  # 原来是草稿时修改状态
                answer.is_draft = checker.validated_data["is_draft"]
            elif checker.validated_data["is_draft"]:
                return self.error(errorcode.MSG_REFORM, errorcode.REFORM)
            with atomic():
                answer.save()
                if not answer.is_draft:  # 正式发表，删除草稿
                    question.answer_set.filter(author=me, is_draft=True).delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeAnswerSerializer(instance=answer, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, question_id, answer_id):
        """查看回答，草稿只有本人可以查看"""

        me = self.get_user_profile(request)
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        answer = Answer.objects.filter(pk=answer_id, question=question_id, is_deleted=False).first()
        if question is None or answer is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if answer.is_draft:
            if me is None or answer.author != me:
                return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        formatter = MeAnswerSerializer(instance=answer, context={"me": me})
        return self.success(formatter.data)


class DraftView(CustomAPIView):
    @logged_in
    def get(self, request):
        """查看本人写的所有回答的草稿，可分页"""

        me = request.me
        qs = Answer.objects.filter(author=me, is_deleted=False, is_draft=True)
        data = self.paginate_data(request, qs, BasicAnswerSerializer)
        return self.success(data)

    @logged_in
    def post(self, request):
        """发表草稿并真实删除其他有关的草稿，无须发送草稿的内容以节省资源"""

        me = request.me
        pk = request.data.get("id")
        try:
            pk = int(pk)
        except:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        answer = Answer.objects.filter(pk=pk, is_deleted=False).first()
        if answer is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if answer.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        if not answer.is_draft:  # 正常情况下不会发生，很可能是测试或攻击
            return self.success()
        try:
            answer.is_draft = False
            with atomic():
                answer.save()
                Answer.objects.filter(author=me, question=answer.question, is_draft=True).delete()
            # TODO 发出相关通知
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class QuestionFollowView(CustomAPIView):
    @logged_in
    def post(self, request, question_id):
        """关注问题，不会重复关注"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            QuestionFollow.objects.get_or_create(user=me, question=question)  # 防止重复关注
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def delete(self, request, question_id):
        """取消关注问题"""

        me = request.me
        qs = QuestionFollow.objects.filter(user=me, question=question_id, is_deleted=False)
        if not qs.exists():
            return self.success()
        try:
            qs.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    def get(self, request):
        """查看某人关注的问题，可分页"""

        me = self.get_user_profile(request)
        slug = request.query_params.get("slug")
        he = self.get_user_by_slug(slug)
        if he is None:
            return self.error(errorcode.MSG_INVALID_SLUG, errorcode.INVALID_SLUG)
        qs = he.followed_questions.filter(is_deleted=False)
        # TODO 是否返回问题的一个回答？
        data = self.paginate_data(request, qs, MeQuestionSerializer, {"me": me})
        return self.success(data)


class InviteView(CustomAPIView):
    @logged_in
    def post(self, request, question_id):
        """邀请回答，不能邀请自己、已经邀请过的用户、已经回答过的用户、主动拒绝的用户"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        slug = request.data.get("slug") or ""
        # 不能邀请自己
        if me.slug == slug:
            return self.error(errorcode.MSG_BAD_INVITE, errorcode.BAD_INVITE)
        he = self.get_user_by_slug(slug)
        if he is None:
            return self.error(errorcode.MSG_INVALID_SLUG, errorcode.INVALID_SLUG)
        # 不能重复邀请同一用户回答同一问题
        if QuestionInvite.objects.filter(inviting=me, invited=he, question=question, is_deleted=False).exists():
            return self.error(errorcode.MSG_BAD_INVITE, errorcode.BAD_INVITE)
        # 不能邀请已回答用户
        if Answer.objects.filter(question=question, author=he, is_deleted=False).exists():
            return self.error(errorcode.MSG_BAD_INVITE, errorcode.BAD_INVITE)
        # TODO 自动拒绝邀请
        # TODO 如果不允许自问自答，则也不能邀请提问者
        try:
            QuestionInvite.objects.create(inviting=me, invited=he, question=question)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class HelperView(CustomAPIView):
    @logged_in
    def get(self, request, question_id):
        """获取可邀请的用户"""

        me = request.me
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # 已经回答的用户
        answered_users = question.answer_set.filter(is_deleted=False).values_list('author')
        # 邀请过的用户
        invited_users = QuestionInvite.objects.filter(question=question, inviting=me, is_deleted=False).values_list(
            "invited")
        # TODO 主动拒绝邀请的用户
        # TODO 问题的作者
        qs = UserProfile.objects.exclude(uid=me.uid).exclude(uid__in=answered_users).exclude(uid__in=invited_users)
        total, max_count = qs.count(), 15
        if total > max_count:  # 用户过多，随机抽取15个
            qs = random.sample(list(qs), max_count)
        data = BasicUserSerializer(instance=qs, many=True).data
        for user in data:
            user["is_invited"] = False
        return self.success(data)
