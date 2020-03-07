from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_identity
from .serializers import IdeaValidator, IdeaDetailSerializer, IdeaCommentValidator, IdeaCommentSerializer
from .models import Idea, IdeaComment, IdeaLike
from apps.userpage.models import UserProfile

from apps.taskapp.tasks import thinks_pv_record


class IdeaView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """发表想法"""

        user_id = request._request.uid
        user = UserProfile.objects.get(uid=user_id)
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
        idea.avatar = user.avatar
        idea.nickname = user.nickname
        s = IdeaDetailSerializer(instance=idea)
        return self.success(s.data)

    @validate_identity
    def get(self, request):
        """查看本人的所有想法"""

        user_id = request._request.uid
        user = UserProfile.objects.get(uid=user_id)
        try:
            ideas = Idea.objects.filter(user_id=user_id)
        except Exception as e:
            return self.error(e.args, 401)
        for idea in ideas:
            idea.avatar = user.avatar
            idea.nickname = user.nickname
        s = IdeaDetailSerializer(instance=ideas, many=True)
        return self.success(s.data)


class MonoIdeaView(CustomAPIView):
    @validate_identity
    def delete(self, request, idea_pk):
        """删除自己的想法"""

        user_id = request._request.uid
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
        user = UserProfile.objects.get(uid=idea.user_id)
        idea.avatar = user.avatar
        idea.nickname = user.nickname
        s = IdeaDetailSerializer(instance=idea)

        # TODO 记录阅读量
        thinks_pv_record.delay(request.META.get('REMOTE_ADDR'), idea.id)
        return self.success(s.data)

    @validate_identity
    def put(self, request, idea_pk):
        """修改自己的想法"""

        user_id = request._request.uid
        user = UserProfile.objects.get(uid=user_id)
        data = {
            "user_id": user_id,
            "content": request.data.get("content", None)
        }
        s = IdeaValidator(data=data)
        s.is_valid()
        if s.errors:
            return self.invalid_serializer(s)
        try:
            idea = Idea.objects.get(pk=idea_pk, user_id=user_id)
            idea.content = s.validated_data["content"]
            idea.save()
        except Exception as e:
            return self.error(e.args, 401)
        idea.avatar = user.avatar
        idea.nickname = user.nickname
        s = IdeaDetailSerializer(instance=idea)
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
            return self.invalid_serializer(s)
        try:
            comment = s.create(s.validated_data)
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)

    def get(self, request, idea_pk):
        """查看想法的所有评论"""

        try:
            idea = Idea.objects.get(pk=idea_pk)
            comments = idea.ideacomment_set.all()
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comments, many=True)
        return self.success(s.data)


class MonoIdeaCommentView(CustomAPIView):
    @validate_identity
    def delete(self, request, idea_pk, comment_pk):
        """删除评论"""

        try:
            IdeaComment.objects.get(pk=comment_pk, user_id=request._request.uid, think=idea_pk).delete()
        except Exception as e:
            return self.error(e.args, 401)
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
            return self.invalid_serializer(s)
        try:
            comment = IdeaComment.objects.get(pk=comment_pk, think=idea_pk, user_id=user_id)
            comment.content = s.validated_data["content"]
            comment.save()
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)

    def get(self, request, idea_pk, comment_pk):
        """查看评论"""

        try:
            comment = IdeaComment.objects.get(pk=comment_pk, think=idea_pk)
        except Exception as e:
            return self.error(e.args, 401)
        s = IdeaCommentSerializer(instance=comment)
        return self.success(s.data)


class IdeaLikeView(CustomAPIView):
    @validate_identity
    def post(self, request):
        """想法及其评论点赞"""

        user_id = request._request.uid
        which_model = Idea if request.data.get("type", "") == "idea" else IdeaComment
        try:
            which_object = which_model.objects.get(pk=request.data.get("id", None))  # TODO 能否给自己点赞
            which_object.agree.create(user_id=user_id)
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()

    @validate_identity
    def delete(self, request):
        """取消点赞"""

        user_id = request._request.uid
        try:
            IdeaLike.objects.get(pk=request.data.get("id", None), user_id=user_id).delete()
        except Exception as e:
            return self.error(e.args, 401)
        return self.success()
