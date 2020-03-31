from django.db.models import Q

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.utils import errorcode
from apps.questions.serializers import QuestionInLabelDiscussSerializer
from .serializers import LabelCreateSerializer, ChildLabelSerializer, LabelUpdateSerializer, LabelDetailSerializer
from .models import Label, LabelFollow


class LabelView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """新建标签"""

        uid = request._request.uid  # TODO 新建标签的权限
        s = LabelCreateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            instance = s.create(s.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)

    def get(self, request):
        """获取所有顶级标签"""

        top_labels = Label.objects.filter(label__isnull=True)
        data = self.paginate_data(request, query_set=top_labels, object_serializer=LabelCreateSerializer)
        return self.success(data)

    @validate_identity
    def delete(self, request):
        """删除标签，同时删除它与其他标签、文章、问答等的关系"""

        uid = request._request.uid  # TODO 删除标签的权限
        label = Label.objects.filter(name=request.GET.get("name", None)).first()
        if not label:
            return self.success()
        if label.article_set.exists() or label.question_set.exists():  # 被文章或问题使用了的标签不可删除，以防它们失去标签
            return self.error(errorcode.MSG_LABEL_USING, errorcode.LABEL_USING)
        try:
            label.delete()  # 与其他标签的父子关系会自动删除
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def put(self, request):
        """修改标签"""

        uid = request._request.uid  # TODO 修改标签的权限
        s = LabelUpdateSerializer(data=request.data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        instance = s.validated_data.pop("old_name")  # 验证后,old_name存放的是标签对象
        instance.name = s.validated_data.get("name")
        instance.intro = s.validated_data.get("intro")
        try:
            instance.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)


class LabelRelationView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """新建标签关系"""

        uid = request._request.uid  # TODO 新建子标签的权限
        parent = Label.objects.filter(name=request.data.get("parent", None)).first()
        child = Label.objects.filter(name=request.data.get("child", None)).first()
        if not parent or not child:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            parent.children.add(child)  # 自动生成的底层数据表有唯一约束，不会重复添加
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success({"parent": parent.name, "child": child.name})

    @validate_identity
    def delete(self, request):
        """删除标签关系"""

        uid = request._request.uid  # TODO 删除子标签的权限
        parent = Label.objects.filter(name=request.GET.get("parent", None)).first()
        child = Label.objects.filter(name=request.GET.get("child", None)).first()
        if not parent or not child:
            return self.success()
        try:
            parent.children.remove(child)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class ChildLabelView(CustomAPIView):
    def get(self, request, pk):
        """根据指定的主键，获取该标签和它的子标签。"""

        parent = Label.objects.filter(pk=pk).first()
        if not parent:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        children = parent.children.all()
        s = ChildLabelSerializer(instance={"parent": parent, "children": children})
        return self.success(s.data)


class LabelFollowView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """关注标签"""

        label = Label.objects.filter(name=request.data.get("name", None)).first()
        if not label:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        try:
            label.labelfollow_set.update_or_create(user_id=request._request.uid, defaults=None)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def delete(self, request):
        """取消关注标签"""

        label = Label.objects.filter(name=request.GET.get("name", None)).first()
        if not label:
            return self.success()
        my_follow = label.labelfollow_set.filter(user_id=request._request.uid).first()
        if not my_follow:
            return self.success()
        try:
            my_follow.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def get(self, request):
        """查看本人关注的标签。"""

        user_id = request._request.uid
        labels = Label.objects.filter(labelfollow__user_id=user_id).all()
        s = LabelCreateSerializer(instance=labels, many=True)
        return self.success(s.data)


class LabelDetailView(CustomAPIView):
    def get(self, request, label_id):
        label = Label.objects.filter(pk=label_id).first()
        if not label:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        s = LabelDetailSerializer(instance=label, context={"me": me})
        return self.success(s.data)


class LabelDiscussView(CustomAPIView):
    def get(self, request, label_id):
        label = Label.objects.filter(pk=label_id).first()
        if not label:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        questions = label.question_set.filter(answer__isnull=False).all()  # TODO 除了要有答案外，还有什么要求？
        s = QuestionInLabelDiscussSerializer(instance=questions, many=True, context={"me": me})
        return self.success(s.data)


class LabelSearchView(CustomAPIView):
    def get(self, request):
        keyword = request.GET.get("kw", "")
        if not keyword:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        labels = Label.objects.filter(Q(name__contains=keyword) | Q(intro__contains=keyword))
        me = self.get_user_profile(request)
        data = [{
            "id": i.pk,
            "name": i.name,
            "intro": i.intro,
            "follower_count": LabelFollow.objects.filter(label=i).count(),
            "item_count": i.article_set.filter(is_deleted=False, status="published").count() + i.question_set.count(),
            "is_followed": False if not me else LabelFollow.objects.filter(label=i, user_id=me.uid).exists()
        } for i in labels]
        return self.success(data)
