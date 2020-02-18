from apps.utils.api import CustomAPIView
from .serializers import LabelCreateSerializer, ChildLabelSerializer, LabelUpdateSerializer
from .models import Label, LabelFollow


class LabelView(CustomAPIView):
    def post(self, request):
        """新建标签，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        s = LabelCreateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            instance = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)

    def get(self, request):
        """获取所有顶级标签。"""

        query_set = Label.objects.filter(label__isnull=True)
        s = LabelCreateSerializer(instance=query_set, many=True)  # TODO 获取更多信息，需要更换序列化器
        return self.success(s.data)

    def delete(self, request):
        """删除标签，同时删除它与其他标签、文章、问答等的关系，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        name = request.data.get("name", None)
        try:
            label = Label.objects.get(name=name)
        except Label.DoesNotExist as e:
            return self.error(e.args, 401)
        try:
            label.delete()  # TODO 与其他标签、文章、问答等的关系是否都自动删除了？
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def put(self, request):
        """修改标签，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        s = LabelUpdateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        instance = s.validated_data.pop("old_name")  # 验证后,old_name存放的是标签对象
        instance.name = s.validated_data.get("name")
        instance.intro = s.validated_data.get("intro")
        try:
            instance.save()
        except Exception as e:
            return self.error(e.args, 401)
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
        except Label.DoesNotExist as e:
            return self.error(e.args, 401)
        try:
            parent.children.add(child)  # 自动生成的底层数据表有唯一约束，不会重复添加
        except Exception as e:
            return self.error(e.args, 401)
        return self.success({"parent": parent.name, "child": child.name})

    def delete(self, request):
        """删除标签关系，需要检查用户权限。"""

        user = request.user  # TODO 检查用户权限

        parent = request.data.get("parent", None)
        child = request.data.get("child", None)
        try:
            parent = Label.objects.get(name=parent)
            child = Label.objects.get(name=child)
        except Label.DoesNotExist as e:
            return self.error(e.args, 401)
        try:
            parent.children.remove(child)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()


class ChildLabelView(CustomAPIView):
    def get(self, request, pk):
        """根据指定的主键，获取该标签和它的子标签。"""

        try:
            parent = Label.objects.get(pk=pk)
        except Label.DoesNotExist as e:
            return self.error(e.args, 401)
        children = parent.children.all()
        s = ChildLabelSerializer(instance={"parent": parent, "children": children})
        return self.success(s.data)


class LabelFollowView(CustomAPIView):
    def post(self, request):
        """关注标签。"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        name = request.data.get("name", None)

        try:
            label = Label.objects.get(name=name)
        except Label.DoesNotExist as e:
            return self.error(e.args, 401)
        try:
            LabelFollow.objects.create(user_id=user_id, label=label)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def delete(self, request):
        """取消关注标签。"""

        user = request.user  # TODO 检查用户权限，只能取消自己关注的标签
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        name = request.data.get("name", None)

        try:
            LabelFollow.objects.get(user_id=user_id, label__name=name).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request):
        """查看关注的标签。"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        follows = LabelFollow.objects.filter(user_id=user_id)
        labels = [i.label for i in follows]
        s = LabelCreateSerializer(instance=labels, many=True)
        return self.success(s.data)
