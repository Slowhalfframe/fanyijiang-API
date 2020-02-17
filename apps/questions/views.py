from apps.utils.api import CustomAPIView

from .serializers import QuestionCreateSerializer
from apps.labels.models import Label


class QuestionView(CustomAPIView):
    def post(self, request):
        """发起提问。"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        who_asks = "步惊云"  # TODO 虚假的名称

        labels = request.data.getlist("labels", [])
        labels = Label.objects.filter(name__in=labels)
        labels = [i.pk for i in labels]
        if not labels:
            return self.error("问题没有标签", 401)

        data = {
            "title": request.data.get("title", None),
            "content": request.data.get("content", None),
            "labels": labels,
        }
        s = QuestionCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        try:
            s.validated_data["user_id"] = user_id
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error("创建问题失败", 401)

        s = QuestionCreateSerializer(instance=instance)
        data = s.data
        data.pop("user_id")
        data["who_asks"] = who_asks
        return self.success(data)
