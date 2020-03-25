from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.userpage.models import UserProfile
from .models import Label
from .serializers import LabelChecker, LabelSerializer


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
        formatter = LabelSerializer(instance=label, context={"me": me})
        return self.success(formatter.data)

    def get(self, request):
        """获取所有顶级标签，可分页"""

        labels = Label.objects.filter(is_deleted=False, parents__isnull=True)
        me = self.get_user_profile(request)
        data = self.paginate_data(request, labels, LabelSerializer, {"me": me})
        return self.success(data)


class OneLabelView(CustomAPIView):
    @validate_identity
    def delete(self, request, label_id):
        """删除标签"""

        # TODO 检查用户权限
        label = Label.objects.filter(pk=label_id).first()
        if not label:
            return self.success()
        # TODO 如果文章或问题使用了该标签，则不应该删除，以防它们失去标签
        try:
            label.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    def put(self, request, label_id):
        """修改标签"""

    def get(self, request, label_id):
        """查看单个标签的详情"""


class ParentLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取父标签，可分页"""


class ChildLabelView(CustomAPIView):
    def get(self, request, label_id):
        """获取子标签，可分页"""
