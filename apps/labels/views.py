from apps.utils.api import CustomAPIView

from .serializers import LabelCreateSerializer
from .models import Label, LabelRelation


class LabelView(CustomAPIView):
    def post(self, request):
        """新建标签，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        s = LabelCreateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        instance = s.create(s.validated_data)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)


class LabelRelationView(CustomAPIView):
    def post(self, request):
        """新建标签关系，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        parent = request.data.get("parent", None)
        child = request.data.get("child", None)
        try:
            parent = Label.objects.get(name=parent)
            child = Label.objects.get(name=child)
        except Label.DoesNotExist:
            return self.error("不存在的标签", 401)

        try:
            LabelRelation.objects.get(parent=parent, child=child)
        except LabelRelation.DoesNotExist:
            LabelRelation.objects.create(parent=parent, child=child)
        else:
            return self.error("关系已经存在", 401)

        return self.success({"parent": parent.name, "child": child.name})

    def delete(self, request):
        """删除标签关系，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        parent = request.data.get("parent", None)
        child = request.data.get("child", None)
        try:
            instance = LabelRelation.objects.get(parent__name=parent, child__name=child)
        except LabelRelation.DoesNotExist:
            pass
        else:
            instance.delete()

        return self.success()
