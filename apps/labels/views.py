from apps.utils.api import CustomAPIView

from .serializers import LabelCreateSerializer


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
