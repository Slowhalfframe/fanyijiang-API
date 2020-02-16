from apps.utils.api import CustomAPIView

from .serializers import LabelCreateSerializer, ChildLabelSerializer, LabelUpdateSerializer
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

    def get(self, request):
        """获取所有顶级标签。"""

        query_set = Label.objects.filter(as_child=None)
        s = LabelCreateSerializer(instance=query_set, many=True)
        return self.success(s.data)

    def delete(self, request):
        """删除标签，同时删除它与其他标签、文章、问答等的关系，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        name = request.data.get("name", None)
        try:
            label = Label.objects.get(name=name)
        except Label.DoesNotExist:
            pass
        else:
            label.delete()  # 关系会自动删除

        return self.success()

    def put(self, request):
        """修改标签，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        s = LabelUpdateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        label = s.validated_data.pop("old_name")  # 验证后,old_name存放的是标签对象
        label.name = s.validated_data.get("name")
        label.intro = s.validated_data.get("intro")
        try:
            label.save()
        except Exception as e:
            return self.error(e, 401)

        s = LabelCreateSerializer(instance=label)
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


class ChildLabelView(CustomAPIView):
    def get(self, request, pk):
        """根据指定的主键，获取该标签和它的子标签。"""

        try:
            parent = Label.objects.get(pk=pk)
        except Label.DoesNotExist:
            return self.error("父标签不存在", 401)

        relations = LabelRelation.objects.filter(parent=parent)
        children = [i.child for i in relations]

        s = ChildLabelSerializer(instance={"parent": parent, "children": children})
        return self.success(s.data)
