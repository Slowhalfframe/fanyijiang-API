from apps.utils.api import CustomAPIView
from .serializers import QuestionCreateSerializer, NewQuestionSerializer


class QuestionView(CustomAPIView):
    def post(self, request):
        """提问"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_asks = "小学生"  # TODO 虚假的名称

        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", None),
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
