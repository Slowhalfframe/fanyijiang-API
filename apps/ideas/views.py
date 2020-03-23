import json

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from apps.utils import errorcode
from apps.userpage.models import UserProfile
from .serializers import IdeaValidator, IdeaDetailSerializer, IdeaCommentValidator, IdeaCommentSerializer
from .models import Idea, IdeaComment

from apps.taskapp.tasks import thinks_pv_record


class IdeaView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """发表想法"""

        user_id = request._request.uid
        avatars = json.dumps(request.data.getlist("avatars", []))
        data = {
            "user_id": user_id,
            "content": request.data.get("content", None),
            "avatars": avatars,
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            idea = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        me = UserProfile.objects.get(pk=user_id)
        s = IdeaDetailSerializer(instance=idea, context={"me": me})
        return self.success(s.data)

    def get(self, request):
        """查看所有想法"""

        ideas = Idea.objects.all()
        me = self.get_user_profile(request)
        data = self.paginate_data(request, query_set=ideas, object_serializer=IdeaDetailSerializer,
                                  serializer_context={"me": me})
        return self.success(data)


class MonoIdeaView(CustomAPIView):
    @validate_identity
    def delete(self, request, idea_pk):
        """删除自己的想法"""

        user_id = request._request.uid
        idea = Idea.objects.filter(pk=idea_pk).first()
        if not idea:
            return self.success()
        if idea.user_id != user_id:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            idea.delete()  # TODO 收藏、点赞等都自动删除了吗
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    def get(self, request, idea_pk):
        """查看想法详情"""

        idea = Idea.objects.filter(pk=idea_pk).first()
        if not idea:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        s = IdeaDetailSerializer(instance=idea, context={"me": me})

        # TODO 记录阅读量
        thinks_pv_record.delay(request.META.get('REMOTE_ADDR'), idea.id)
        return self.success(s.data)

    @validate_identity
    def put(self, request, idea_pk):
        """修改自己的想法"""

        user_id = request._request.uid
        avatars = json.dumps(request.data.getlist("avatars", []))
        data = {
            "user_id": user_id,
            "content": request.data.get("content", None),
            "avatars": avatars,
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        idea = Idea.objects.filter(pk=idea_pk).first()
        if not idea:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if idea.user_id != user_id:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            idea.content = s.validated_data["content"]
            idea.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        me = UserProfile.objects.get(pk=user_id)
        s = IdeaDetailSerializer(instance=idea, context={"me": me})
        return self.success(s.data)


class IdeaCommentView(CustomAPIView):
    @validate_identity
    def post(self, request, idea_pk):
        """想法评论"""

        data = {
            "user_id": request._request.uid,
            "think": idea_pk,
            "content": request.data.get("content", None)
        }
        s = IdeaCommentValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            comment = s.create(s.validated_data)
        except Exception as e:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        me = UserProfile.objects.get(pk=data["user_id"])
        s = IdeaCommentSerializer(instance=comment, context={"me": me})
        return self.success(s.data)

    def get(self, request, idea_pk):
        """查看想法的所有评论"""

        idea = Idea.objects.filter(pk=idea_pk).first()
        if not idea:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        comments = idea.ideacomment_set.all()
        me = self.get_user_profile(request)
        data = self.paginate_data(request, query_set=comments, object_serializer=IdeaCommentSerializer,
                                  serializer_context={"me": me})
        return self.success(data)


class MonoIdeaCommentView(CustomAPIView):
    @validate_identity
    def delete(self, request, idea_pk, comment_pk):
        """删除评论"""

        comment = IdeaComment.objects.filter(pk=comment_pk, think=idea_pk).first()
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
    def put(self, request, idea_pk, comment_pk):
        """修改评论"""

        user_id = request._request.uid
        data = {
            "user_id": user_id,
            "think": idea_pk,
            "content": request.data.get("content", None)
        }
        s = IdeaCommentValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        comment = IdeaComment.objects.filter(pk=comment_pk, think=idea_pk).first()
        if not comment:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        if comment.user_id != user_id:
            return self.error(errorcode.MSG_NOT_OWNER, errorcode.NOT_OWNER)
        try:
            comment.content = s.validated_data["content"]
            comment.save()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        me = UserProfile.objects.get(pk=user_id)
        s = IdeaCommentSerializer(instance=comment, context={"me": me})
        return self.success(s.data)

    def get(self, request, idea_pk, comment_pk):
        """查看评论"""

        comment = IdeaComment.objects.filter(pk=comment_pk, think=idea_pk).first()
        if not comment:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        me = self.get_user_profile(request)
        s = IdeaCommentSerializer(instance=comment, context={"me": me})
        return self.success(s.data)


class IdeaLikeView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """想法及其评论点赞"""

        which_model = Idea if request.data.get("type", "") == "idea" else IdeaComment
        which_object = which_model.objects.filter(pk=request.data.get("id", None)).first()
        if not which_object:
            return self.error(errorcode.MSG_NO_DATA, errorcode.NO_DATA)
        # TODO 能否给自己点赞
        try:
            which_object.agree.update_or_create(user_id=request._request.uid, defaults=None)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()

    @validate_identity
    def delete(self, request):
        """取消点赞"""

        which_model = Idea if request.GET.get("type", "") == "idea" else IdeaComment
        which_object = which_model.objects.filter(pk=request.GET.get("id", None)).first()
        if not which_object:
            return self.success()
        mylike = which_object.agree.filter(user_id=request._request.uid).first()
        if not mylike:
            return self.success()
        try:
            mylike.delete()
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        return self.success()
