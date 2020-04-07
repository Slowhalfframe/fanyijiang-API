from apps.utils import errorcode
from apps.utils.api import CustomAPIView
from apps.utils.decorators import logged_in
from .models import Idea
from .serializers import IdeaChecker, MeIdeaSerializer


class IdeaView(CustomAPIView):
    @logged_in
    def post(self, request):
        """写想法"""

        me = request.me
        data = {
            "content": request.data.get("content") or "",
            "avatars": request.data.get("avatars") or "[]",
        }
        checker = IdeaChecker(data=data)
        checker.is_valid()
        if checker.errors:
            return self.error(errorcode.MSG_INVALID_DATA, errorcode.INVALID_DATA)
        try:
            idea = Idea.objects.create(author=me, **checker.validated_data)
        except:
            return self.error(errorcode.MSG_DB_ERROR, errorcode.DB_ERROR)
        formatter = MeIdeaSerializer(instance=idea, context={"me": me})
        return self.success(formatter.data)

    @logged_in
    def get(self, request):
        """查看某人的想法，必须登录，可分页"""

        me = request.me
        slug = request.query_params.get("slug")
        he = self.get_user_by_slug(slug)
        if he is None:
            return self.error(errorcode.MSG_INVALID_SLUG, errorcode.INVALID_SLUG)
        qs = Idea.objects.filter(author=he, is_deleted=False)
        data = self.paginate_data(request, qs, MeIdeaSerializer, {"me": me})
        return self.success(data)
