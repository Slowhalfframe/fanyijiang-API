from apps.utils.api import CustomAPIView
from .serializers import ArticleCreateSerializer, NewArticleSerializer


class ArticleView(CustomAPIView):
    def post(self, request):
        """发表文章"""

        user = request.user  # TODO 检查用户权限
        user_id = "cd2ed05828ebb648a225c35a9501b007"  # TODO 虚假的ID

        data = {
            "user_id": user_id,
            "title": request.data.get("title", None),
            "content": request.data.get("content", None),  # 注意HTML转义
            "image": request.data.get("image", ""),
            "status": request.data.get("status", "draft"),
            "labels": request.data.getlist("labels", []),
        }
        s = ArticleCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)

        try:
            article = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = NewArticleSerializer(instance=article)
        return self.success(s.data)
