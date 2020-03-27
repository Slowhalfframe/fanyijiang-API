from django.db.transaction import atomic

from apps.labels_v2.models import Label
from apps.questions_v2.models import Question
from apps.questions_v2.serializers import QuestionChecker, MeQuestionSerializer
from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in


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
        """查看问题的详情"""

        me = self.get_user_profile(request)
        question = Question.objects.filter(pk=question_id, is_deleted=False).first()
        if question is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        formatter = MeQuestionSerializer(instance=question, context={"me": me})
        # TODO 返回一批回答
        return self.success(formatter.data)
