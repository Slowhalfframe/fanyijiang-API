from django.db import transaction

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.utils import errorcode
from apps.userpage.models import UserProfile
from .serializers import ArticleCreateSerializer, NewArticleSerializer, ArticleDetailSerializer, \
    ArticleCommentSerializer
from .models import Article, ArticleComment

from apps.taskapp.tasks import articles_pv_record, notification_handler


class ArticleView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """发表文章"""

        data = {
            "user_id": request._request.uid,
            "title": request.data.get("title", None),
            "content": request.data.get("content", None),  # 注意HTML转义
            "image": request.data.get("image", ""),
            "status": request.data.get("status", "draft"),
            "labels": request.data.getlist("labels", []),
        }
        s = ArticleCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            article = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = NewArticleSerializer(instance=article)
        return self.success(s.data)

    @validate_identity
    def put(self, request):
        """更新文章，成品不能改为草稿"""

        user_id = request._request.uid
        article = Article.objects.filter(pk=request.data.get("id", None), is_deleted=False).first()
        if not article:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if article.user_id != user_id:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        data = {
            "user_id": user_id,
            # TODO 使用序列化器来验证数据，需要绕过作者和标题的唯一性，因此使用假标题。
            # TODO 这会造成BUG：用户发表了标题为a的文章后，就不能更新自己的文章了
            "title": "a",
            "content": request.data.get("content", None),  # 注意HTML转义
            "image": request.data.get("image", ""),
            "status": request.data.get("status", "draft"),
            "labels": request.data.getlist("labels", []),
        }
        s = ArticleCreateSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        title = request.data.get("title", "")
        if not title:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        status = s.validated_data["status"]
        if article.status == "published":
            status = "published"

        article.title = title
        article.content = s.validated_data["content"]
        article.image = s.validated_data["image"]
        article.status = status
        try:
            with transaction.atomic():
                article.save()
                article.labels.set(s.validated_data["labels"])
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = NewArticleSerializer(instance=article)
        return self.success(s.data)

    @validate_identity
    def patch(self, request):
        """把草稿变为成品"""

        article = Article.objects.filter(pk=request.data.get("id", None), is_deleted=False).first()
        if not article:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if article.user_id != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        if article.status == "draft":
            if not article.labels.exists():
                return self.error(errorcode.MSG_NO_LABELS, errorcode.NO_LABELS)
            article.status = "published"
            try:
                article.save()
            except:
                return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    def get(self, request):
        """查看文章，不包括草稿"""

        articles = Article.objects.filter(status="published", is_deleted=False)
        # TODO 返回哪部分数据？
        data = self.paginate_data(request, query_set=articles, object_serializer=NewArticleSerializer)
        return self.success(data)


class ArticleDetailView(CustomAPIView):
    def get(self, request, article_id):
        """查看文章详情，只有作者能查看草稿"""

        article = Article.objects.filter(pk=article_id, is_deleted=False).first()
        if not article:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if article.status == "draft":
            me = self.get_user_profile(request)
            if not me:
                return self.error(errorcode.MSG_LOGIN_REQUIRED, errorcode.LOGIN_REQUIRED)
            if article.user_id != me.uid:
                return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        me = self.get_user_profile(request)
        s = ArticleDetailSerializer(instance=article, context={"me": me})

        # TODO 记录阅读量
        articles_pv_record.delay(request.META.get('REMOTE_ADDR'), article.id)
        return self.success(s.data)

    @validate_identity
    def delete(self, request, article_id):
        """删除文章"""

        article = Article.objects.filter(pk=article_id, is_deleted=False).first()
        if not article:
            return self.success()
        if article.user_id != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        article.is_deleted = True
        try:
            article.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class DraftView(CustomAPIView):
    @validate_identity
    def get(self, request):
        """查看草稿箱"""

        drafts = Article.objects.filter(user_id=request._request.uid, status="draft", is_deleted=False)
        # TODO 返回哪部分数据？
        data = self.paginate_data(request, query_set=drafts, object_serializer=ArticleDetailSerializer)
        return self.success(data)


class CommentView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """评论文章，必须是已发表的文章"""

        data = {
            "article": request.data.get("id", None),
            "user_id": request._request.uid,
            "content": request.data.get("content", None),
        }
        s = ArticleCommentSerializer(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        article = s.validated_data["article"]
        s.validated_data["reply_to_user"] = article.user_id
        try:
            comment = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = ArticleCommentSerializer(instance=comment, context={"me": UserProfile.objects.get(pk=request._request.uid)})

        # TODO 触发消息通知
        # 某人评论了你的文章
        notification_handler.delay(request._request.uid, article.user_id, 'CAR', comment.id)
        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """删除本人的评论"""

        comment = ArticleComment.objects.filter(pk=request.GET.get("id", None)).first()
        if not comment:
            return self.success()
        if comment.user_id != request._request.uid:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            comment.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def put(self, request):
        """修改本人的评论"""

        user_id = request._request.uid
        content = request.data.get("content", None)
        if not content:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        comment = ArticleComment.objects.filter(pk=request.data.get("id", None)).first()
        if not comment:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if comment.user_id != user_id:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            comment.content = content
            comment.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = ArticleCommentSerializer(instance=comment)
        return self.success(s.data)


class VoteView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """文章及其评论的投票"""

        user_id = request._request.uid
        which_model = Article if request.data.get("type", "") == "article" else ArticleComment
        which_object = which_model.objects.filter(pk=request.data.get("id", None)).first()
        if not which_object:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # TODO 能否给自己投票
        value = request.data.get("value", "0")
        value = bool(int(value))  # value采用数字
        try:
            which_object.vote.update_or_create(user_id=user_id, defaults={"value": value})
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        # TODO 触发消息通知
        if which_model == Article and value == True:
            # 给文章点赞
            notification_handler.delay(user_id, which_object.user_id, 'LAR', which_object.id)
        elif which_model == ArticleComment and value == True:
            # 给文章评论点赞
            notification_handler.delay(user_id, which_object.user_id, 'LAC', which_object.id)
        return self.success()

    @validate_identity
    def delete(self, request):
        """撤销投票"""

        user_id = request._request.uid
        which_model = Article if request.GET.get("type", "") == "article" else ArticleComment
        which_object = which_model.objects.filter(pk=request.GET.get("id", None)).first()
        if not which_object:
            return self.success()
        old_vote = which_object.vote.filter(user_id=user_id).first()
        if not old_vote:
            return self.success()
        try:
            old_vote.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class ArticleCommentDetailView(CustomAPIView):
    def get(self, request, article_id):
        """获取指定文章的所有评论"""

        article = Article.objects.filter(pk=article_id, status="published", is_deleted=False).first()
        if not article:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        comments = article.articlecomment_set.all()  # TODO 过滤条件
        me = self.get_user_profile(request)
        data = self.paginate_data(request, query_set=comments, object_serializer=ArticleCommentSerializer,
                                  serializer_context={"me": me})
        return self.success(data)
