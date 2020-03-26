from apps.userpage.models import UserProfile
from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from .models import Label, LabelFollow
from .serializers import LabelChecker, SimpleLabelSerializer, DetailedLabelSerializer


class LabelView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """新建标签"""

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
        me = UserProfile.objects.get(uid=request._request.uid)
        formatter = SimpleLabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)

    def get(self, request):
        """获取所有顶级标签，可分页"""

        qs = Label.objects.filter(is_deleted=False, parents__isnull=True)
        me = self.get_user_profile(request)
        data = self.paginate_data(request, qs, SimpleLabelSerializer, {"me": me})
        return self.success(data)


class OneLabelView(CustomAPIView):
    @validate_identity
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

    @validate_identity
    def put(self, request, label_id):
        """修改标签"""

        # TODO 检查用户权限
        qs = Label.objects.filter(pk=label_id, is_deleted=False)
        if not qs.exists():
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
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
            qs.update(**checker.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        me = UserProfile.objects.get(uid=request._request.uid)
        formatter = SimpleLabelSerializer(instance=qs.get(), context={"me": me})
        return self.success(formatter.data)

    def get(self, request, label_id):
        """查看单个标签的详情"""

        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        formatter = DetailedLabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)


class ParentLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取父标签，可分页"""

        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        qs = label.parents.filter(is_deleted=False)
        data = self.paginate_data(request, qs, SimpleLabelSerializer, {"me": me})
        return self.success(data)


class ChildLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取子标签，可分页"""

        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        qs = label.children.filter(is_deleted=False)
        data = self.paginate_data(request, qs, SimpleLabelSerializer, {"me": me})
        return self.success(data)

    @validate_identity
    def post(self, request, label_id):
        """添加子标签"""

        # TODO 检查用户权限
        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        pk = request.data.get("id") or None
        child = Label.objects.filter(pk=pk, is_deleted=False).first()
        if label is None or child is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            label.children.add(child)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
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
    @validate_identity
    def post(self, request, label_id):
        """关注标签，不会重复关注"""

        label = Label.objects.filter(pk=label_id, is_deleted=False).first()
        if label is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = UserProfile.objects.get(uid=request._request.uid)
        try:
            LabelFollow.objects.get_or_create(user=me, label=label)  # 防止重复关注
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def delete(self, request, label_id):
        """取消关注标签"""

        uid = request._request.uid
        qs = LabelFollow.objects.filter(user__uid=uid, label_id=label_id, is_deleted=False)
        try:
            qs.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()
