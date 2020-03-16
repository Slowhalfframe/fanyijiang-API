from django.conf import settings
import requests

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
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)

    def get(self, request):
        """获取所有顶级标签。"""

        query_set = Label.objects.filter(label__isnull=True)
        s = LabelCreateSerializer(instance=query_set, many=True)  # TODO 获取更多信息，需要更换序列化器
        return self.success(s.data)

    @validate_identity
    def delete(self, request):
        """删除标签，同时删除它与其他标签、文章、问答等的关系"""

        uid = request._request.uid  # TODO 删除标签的权限
        name = request.data.get("name", None)
        try:
            label = Label.objects.get(name=name)
            label.delete()  # TODO 与其他标签、文章、问答等的关系都自动删除了，可能使文章、问答等失去标签
        except Label.DoesNotExist:
            pass
        except Exception as e:
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
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = LabelCreateSerializer(instance=instance)
        return self.success(s.data)


class LabelRelationView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """新建标签关系"""

        uid = request._request.uid  # TODO 新建子标签的权限
        parent = request.data.get("parent", None)
        child = request.data.get("child", None)
        try:
            parent = Label.objects.get(name=parent)
            child = Label.objects.get(name=child)
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            parent.children.add(child)  # 自动生成的底层数据表有唯一约束，不会重复添加
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success({"parent": parent.name, "child": child.name})

    @validate_identity
    def delete(self, request):
        """删除标签关系"""

        uid = request._request.uid  # TODO 删除子标签的权限
        parent = request.data.get("parent", None)
        child = request.data.get("child", None)
        try:
            parent = Label.objects.get(name=parent)
            child = Label.objects.get(name=child)
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            parent.children.remove(child)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()


class ChildLabelView(CustomAPIView):
    def get(self, request, pk):
        """根据指定的主键，获取该标签和它的子标签。"""

        try:
            parent = Label.objects.get(pk=pk)
            children = parent.children.all()
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        except Exception:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        s = ChildLabelSerializer(instance={"parent": parent, "children": children})
        return self.success(s.data)


class LabelFollowView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """关注标签。"""

        user_id = request._request.uid
        name = request.data.get("name", None)
        try:
            label = Label.objects.get(name=name)
            LabelFollow.objects.create(user_id=user_id, label=label)
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def delete(self, request):
        """取消关注标签。"""

        user_id = request._request.uid
        name = request.data.get("name", None)
        try:
            LabelFollow.objects.get(user_id=user_id, label__name=name).delete()  # 只能取消自己关注的标签
        except LabelFollow.DoesNotExist:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.INVALID_DATA)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def get(self, request):
        """查看本人关注的标签。"""

        user_id = request._request.uid
        follows = LabelFollow.objects.filter(user_id=user_id)
        labels = [i.label for i in follows]
        s = LabelCreateSerializer(instance=labels, many=True)
        return self.success(s.data)


class LabelDetailView(CustomAPIView):
    def get(self, request, label_id):
        try:
            label = Label.objects.get(pk=label_id)
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        url = settings.USER_CENTER_GATEWAY + '/api/verify'
        headers = {'authorization': request.META.get("HTTP_AUTHORIZATION")}
        try:
            res = requests.get(url=url, headers=headers)
            res_data = res.json()
            me = res_data['data']
        except:
            me = ""
        s = LabelDetailSerializer(instance=label, context={"me": me})  # me是用户的UID或者空字符串，表示谁登录或无人登录
        return self.success(s.data)


class LabelDiscussView(CustomAPIView):
    def get(self, request, label_id):
        try:
            label = Label.objects.get(pk=label_id)
        except Label.DoesNotExist:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        url = settings.USER_CENTER_GATEWAY + '/api/verify'
        headers = {'authorization': request.META.get("HTTP_AUTHORIZATION")}
        try:
            res = requests.get(url=url, headers=headers)
            res_data = res.json()
            me = res_data['data']
        except:
            me = ""
        questions = label.question_set.filter(answer__isnull=False).all()  # TODO 除了要有答案外，还有什么要求？
        s = QuestionInLabelDiscussSerializer(instance=questions, many=True, context={"me": me})
        return self.success(s.data)
