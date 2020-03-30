from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in
from apps.labels_v2.models import Label
from apps.utils import errorcode
from .serializers import ArticleChecker, MeArticleSerializer
from django.db.transaction import atomic
from .models import Article


class ArticleView(CustomAPIView):
    @logged_in
    def post(self, request):
        """写文章，可以是草稿"""

        me = request.me
        # TODO 检查用户权限
        data = {
            "title": request.data.get("title") or "",
            "content": request.data.get("content") or "",
            "thumbnail": request.data.get("thumbnail") or None,
            "status": request.data.get("status") or None,
        }
        # 请求体为空时,request.data为普通的空字典，没有getlist方法
        if "labels" not in request.data:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        labels = request.data.getlist("labels") or []
        try:  # labels里有非数字时会导致查询出错
            qs = Label.objects.filter(pk__in=labels)
        except:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        if not qs.exists():
            return self.error(errorcode.MSG_NO_LABELS, errorcode.NO_LABELS)
        checker = ArticleChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            with atomic():
                article = Article.objects.create(author=me, **checker.validated_data)
                article.labels.add(*(i for i in qs))
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeArticleSerializer(instance=article, context={"me": me})
        return self.success(formatter.data)
