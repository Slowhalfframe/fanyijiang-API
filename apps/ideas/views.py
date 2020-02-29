from apps.utils.api import CustomAPIView

from .serializers import IdeaValidator, IdeaDetailSerializer
from .models import Idea


class IdeaView(CustomAPIView):
    def post(self, request):
        """发表想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称

        data = {
            "user_id": user_id,
            "content": request.data.get("content", None)
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            idea = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        idea.avatar = avatar
        idea.nickname = nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)


class MonoIdeaView(CustomAPIView):
    def delete(self, request, idea_pk):
        """删除自己的想法"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        try:
            idea = Idea.objects.get(pk=idea_pk, user_id=user_id)
            idea.delete()  # TODO 收藏、点赞等都自动删除了吗
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    def get(self, request, idea_pk):
        """查看想法详情"""

        try:
            idea = Idea.objects.get(pk=idea_pk)
        except Idea.DoesNotExist as e:
            return self.error(e.args, 401)
        avatar = "images/001.png"  # TODO 虚假的头像
        nickname = "新手"  # TODO 虚假的昵称
        idea.avatar = avatar
        idea.nickname = nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)
