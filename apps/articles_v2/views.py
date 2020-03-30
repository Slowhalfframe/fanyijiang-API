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
            "is_draft": request.data.get("is_draft") or None,
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


class OneArticleView(CustomAPIView):
    @logged_in
    def delete(self, request, article_id):
        """删除本人的文章，草稿会真实删除，正式文章不能随意删除"""

        me = request.me
        article = Article.objects.filter(pk=article_id, is_deleted=False).first()
        if article is None:
            return self.success()
        if article.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        # TODO 什么文章不能删除？
        try:
            if article.is_draft:
                article.delete()
            else:
                article.is_deleted = True
                article.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @logged_in
    def put(self, request, article_id):
        """修改本人的文章，也可以同时正式发表，不会删除其他草稿，绝不允许把发表的文章变成草稿"""

        me = request.me
        article = Article.objects.filter(pk=article_id, is_deleted=False).first()
        if article is None:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if article.author != me:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        data = {
            "title": request.data.get("title") or "",
            "content": request.data.get("content") or "",
            "thumbnail": request.data.get("thumbnail") or None,
            "is_draft": request.data.get("is_draft") or None,
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
            article.title = checker.validated_data["title"]
            article.content = checker.validated_data["content"]
            article.thumbnail = checker.validated_data["thumbnail"]
            if article.is_draft:
                article.is_draft = checker.validated_data["is_draft"]
            elif checker.validated_data["is_draft"]:
                return self.error(errorcode.MSG_REFORM, errorcode.REFORM)
            with atomic():
                article.save()
                article.labels.clear()
                article.labels.add(*(i for i in qs))
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeArticleSerializer(instance=article, context={"me": me})
        return self.success(formatter.data)

    def get(self, request, article_id):
        """查看文章详情"""
        pass
