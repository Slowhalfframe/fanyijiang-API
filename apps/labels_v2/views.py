from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in
from .models import Label, LabelFollow
from .serializers import LabelChecker, StatLabelSerializer, MeLabelSerializer


class LabelView(CustomAPIView):
    @logged_in
    def post(self, request):
        """新建标签"""

        me = request.me
        # TODO 检查用户权限
        data = {
            "name": request.data.get("name") or "",
            "intro": request.data.get("intro") or "",
            "avatar": request.data.get("avatar") or "",
        }
        checker = LabelChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            label = checker.create(checker.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeLabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)

    def get(self, request):
        """获取所有顶级标签，可分页"""

        me = self.get_user_profile(request)
        qs = Label.objects.filter(is_deleted=False, parents__isnull=True)
        data = self.paginate_data(request, qs, MeLabelSerializer, {"me": me})
        return self.success(data)


class OneLabelView(CustomAPIView):
    @logged_in
    def delete(self, request, label_id):
        """删除标签"""

        # TODO 检查用户权限
        qs = Label.objects.filter(pk=label_id, is_deleted=False)  # 故意使用查询集而非标签
        if not qs.exists():
            return self.success()
        # TODO 如果文章或问题使用了该标签，则不应该删除，以防它们失去标签
        try:
            qs.delete()  # TODO 是否逻辑删除？
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def put(self, request, label_id):
        """修改标签"""

        me = request.me
        # TODO 检查用户权限
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        name = request.data.get("name") or ""
        data = {
            "intro": request.data.get("intro") or "",
            "avatar": request.data.get("avatar") or "",
            "name": "a" if label.name == name else name  # 标签名称不变时，绕过唯一性验证
        }
        checker = LabelChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        label.intro = checker.validated_data["intro"]
        label.avatar = checker.validated_data["avatar"]
        if not label.name == name:
            label.name = checker.validated_data["name"]
        try:
            label.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeLabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, label_id):
        """查看单个标签的详情"""

        me = self.get_user_profile(request)
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        formatter = MeLabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)


class ParentLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取父标签，可分页"""

        me = self.get_user_profile(request)
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        qs = label.parents.filter(is_deleted=False)
        data = self.paginate_data(request, qs, StatLabelSerializer, {"me": me})
        return self.success(data)


class ChildLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取子标签，可分页"""

        me = self.get_user_profile(request)
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        qs = label.children.filter(is_deleted=False)
        data = self.paginate_data(request, qs, StatLabelSerializer, {"me": me})
        return self.success(data)

    @logged_in
    def post(self, request, label_id):
        """添加子标签"""

        # TODO 检查用户权限
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        pk = request.data.get("id") or None
        child = Label.objects.filter(pk=pk, is_deleted=False).first()
        if label is None or child is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if label.pk == child.pk:  # 不能以自己为子标签
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            label.children.add(child)  # 自动避免重复
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def delete(self, request, label_id):
        """删除子标签"""

        # TODO 检查用户权限
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.success()
        pk = request.query_params.get("id") or request.data.get("id") or None
        child = Label.objects.filter(pk=pk, is_deleted=False).first()
        try:
            label.children.remove(child)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class LabelFollowView(CustomAPIView):
    @logged_in
    def post(self, request, label_id):
        """关注标签，不会重复关注"""

        me = request.me
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            LabelFollow.objects.get_or_create(user=me, label=label)  # 防止重复关注
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def delete(self, request, label_id):
        """取消关注标签"""

        me = request.me
        qs = LabelFollow.objects.filter(user=me, label_id=label_id, is_deleted=False)
        try:
            qs.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    def get(self, request):
        """查看某个用户关注的标签，可分页"""

        me = self.get_user_profile(request)
        slug = request.query_params.get("slug")
        he = self.get_user_by_slug(slug)
        if he is None:
            return self.error(errorcode.MSG_INVALID_SLUG, errorcode.INVALID_SLUG)
        qs = he.followed_labels.filter(is_deleted=False)
        data = self.paginate_data(request, qs, MeLabelSerializer, {"me": me})
        return self.success(data)


class LabelDiscussionView(CustomAPIView):
    def get(self, request, label_id):
        """获取本标签的讨论内容，或者说热点"""

        # TODO 未实现，需要先实现文章、问答等的模型
