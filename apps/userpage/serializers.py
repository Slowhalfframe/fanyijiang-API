from rest_framework import serializers
from django.conf import settings
import json

from apps.userpage.models import (UserProfile, UserEmploymentHistory, UserEducationHistory, FollowedUser,
                                  UserLocations, UserFavorites, FollowedFavorites, FavoriteCollection)

from apps.labels.models import Label

from apps.questions.models import Question, QuestionFollow, Answer

from apps.articles.models import Article

from apps.pins.models import Idea


class UserInfoSerializer(serializers.ModelSerializer):
    employment_history = serializers.SerializerMethodField()
    education_history = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('uid', 'nickname', 'avatar', 'autograph', 'gender', 'industry',
                  'employment_history', 'education_history', 'locations',
                  'description', 'slug', 'page_image')

    def get_employment_history(self, obj):
        history = obj.user_employment_history.all()
        data = UserEmploymentHistorySerializer(history, many=True).data
        return data

    def get_education_history(self, obj):
        history = obj.user_education_history.all()
        data = UserEducationHistorySerializer(history, many=True).data
        return data

    def get_locations(self, obj):
        locations = obj.location.all()
        data = UserLocationSerializer(locations, many=True).data
        return data


class UserEmploymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmploymentHistory
        fields = ('company', 'position')


class UserEducationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducationHistory
        fields = ('school', 'major', 'education', 'in_year', 'out_year')


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocations
        fields = ('name', 'location_pic')


class FavoritesSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()
    follow_count = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    owner_info = serializers.SerializerMethodField()

    # update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="update_time", read_only=True)

    class Meta:
        model = UserFavorites
        fields = ('id', 'title', 'status', 'content_count', 'follow_count', 'update_time', 'is_followed', 'owner_info')

    def get_content_count(self, obj):
        return obj.favorite_collect.all().count()

    def get_follow_count(self, obj):
        return FollowedFavorites.objects.filter(fa=obj).count()

    def get_owner_info(self, obj):
        owner = obj.user
        data = {'nickname': owner.nickname, 'slug': owner.slug}
        return data

    def get_is_followed(self, obj):
        uid = self.context['uid']
        data = False
        if FollowedFavorites.objects.filter(user_id=uid, fa=obj).exists():
            data = True
        return data


class ContentFavoritesSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()
    follow_count = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    # update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="update_time", read_only=True)

    class Meta:
        model = UserFavorites
        fields = (
        'id', 'title', 'status', 'intro', 'content_count', 'follow_count', 'update_time', 'is_followed', 'is_owner')

    def get_content_count(self, obj):
        return obj.favorite_collect.all().count()

    def get_follow_count(self, obj):
        return FollowedFavorites.objects.filter(fa=obj).count()

    def get_is_owner(self, obj):
        uid = self.context.get('uid')
        if obj.user.uid == uid:
            return True
        return False

    # def get_owner_info(self, obj):
    #     owner = obj.user
    #     data = {'nickname': owner.nickname, 'slug': owner.slug}
    #     return data
    #
    def get_is_followed(self, obj):
        uid = self.context['uid']
        data = False
        if FollowedFavorites.objects.filter(user_id=uid, fa=obj).exists():
            data = True
        return data


# class FavoritesAnswerSerializer(serializers.ModelSerializer):
#     class Meta:


class FollowsUserSerializer(serializers.ModelSerializer):
    fans_count = serializers.SerializerMethodField()  # 关注者
    articles_count = serializers.SerializerMethodField()  # 文章数
    answers_count = serializers.SerializerMethodField()  # 回答数
    text = serializers.CharField(source="nickname")

    class Meta:
        model = UserProfile
        fields = ('avatar', 'nickname', 'autograph', 'slug', 'uid', 'fans_count', 'articles_count', 'answers_count',"text")

    def get_fans_count(self, obj):
        return UserProfile.objects.filter(as_fans__idol__uid=obj.uid).count()

    def get_articles_count(self, obj):
        # TODO 数据库查询
        return Article.objects.filter(author_id=obj.uid, is_draft=False, is_deleted=False).count()

    def get_answers_count(self, obj):
        # TODO 数据库查询
        return Answer.objects.filter(author_id=obj.uid).count()


class FavoritesContentSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteCollection
        fields = ('details',)

    def get_details(self, obj):
        content_object = obj.content_object
        content_data = None
        me = self.context["me"]
        if isinstance(content_object, Answer):
            content_data = UserPageAnswerSerializer(instance=content_object, context=self.context).data
            content_data['data_type'] = 'answer'
        if isinstance(content_object, Article):
            content_data = UserPageArticleSerializer(instance=content_object, context=self.context).data
            content_data['data_type'] = 'article'
        if isinstance(content_object, Idea):
            content_data = UserPageThinksSerializer(instance=content_object, context=self.context).data
            content_data['data_type'] = 'think'
        return content_data


class UserPageQuestionSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="create_at", read_only=True)
    answer_count = serializers.SerializerMethodField()
    follow_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'create_time', 'answer_count', 'follow_count')

    def get_answer_count(self, obj):
        return obj.answer_set.all().count()

    def get_follow_count(self, obj):
        return QuestionFollow.objects.filter(question=obj).count()


class UserPageAnswerSerializer(serializers.ModelSerializer):
    question_title = serializers.SerializerMethodField()
    top_answer = serializers.SerializerMethodField()
    currentUserVote = serializers.SerializerMethodField()
    update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="create_at", read_only=True)
    data_type = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('question_id', 'question_title', 'top_answer', 'currentUserVote', 'update_time', 'data_type')

    def get_top_answer(self, obj):
        data = AnswerInLabelDiscussSerializer(obj, context=self.context).data
        return data

    def get_question_title(self, obj):
        return obj.question.title

    def get_currentUserVote(self, obj):
        """返回None表示未投票，True表示赞成，False表示反对"""
        me = self.context["me"]  # None或者当前登录的UserProfile对象
        if not me:
            # <<<<<<< master
            return None
        my_vote = obj.votes.filter(author_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_data_type(self, obj):
        return 'answer'


class UserPageArticleSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="update_at", read_only=True)
    comment_count = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    currentUserVote = serializers.SerializerMethodField()
    data_type = serializers.SerializerMethodField()


    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'image', 'update_time', 'comment_count', 'upvote_count', 'author_info',
                  'currentUserVote', 'data_type')

    def get_comment_count(self, obj):
        return obj.comments.all().count()

    def get_upvote_count(self, obj):
        return obj.votes.filter(value=True).count()

    def get_author_info(self, obj):
        author = UserProfile.objects.filter(uid=obj.author_id).first()
        data = {
            'avatar': author.avatar,
            'nickname': author.nickname,
            'slug': author.slug,
            'autograph': author.autograph,
        }
        return data

    def get_currentUserVote(self, obj):
        """返回None表示未投票，True表示赞成，False表示反对"""
        me = self.context["me"]  # None或者当前登录的UserProfile对象
        if not me:
            # <<<<<<< master
            return None
        my_vote = obj.votes.filter(author_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_data_type(self, obj):
        return 'article'


class UserPageThinksSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="create_at", read_only=True)
    comment_count = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    avatars = serializers.SerializerMethodField()
    currentUserVote = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = (
        'id', 'content', 'create_time', 'comment_count', 'upvote_count', 'author_info', 'avatars', 'currentUserVote')

    def get_comment_count(self, obj):
        return obj.comments.all().count()

    def get_upvote_count(self, obj):
        return obj.agree.all().count()

    def get_author_info(self, obj):
        author = UserProfile.objects.filter(uid=obj.author_id).first()
        data = {
            'avatar': author.avatar,
            'nickname': author.nickname,
            'slug': author.slug,
            'autograph': author.autograph,
        }
        return data

    def get_avatars(self, obj):
        picture = obj.avatars
        if len(picture):
            # data = picture.replace('[', '').replace(']','').replace('\"', '').split(',')
            data = json.loads(picture)
            data = [settings.PICTURE_HOST + p for p in data]
            return data
        return None

    def get_currentUserVote(self, obj):
        """返回None表示未投票，True表示赞成，False表示反对"""
        me = self.context["me"]  # None或者当前登录的UserProfile对象
        if not me:
            # <<<<<<< master
            return None
        my_vote = obj.votes.filter(author_id=me.uid).first()
        if not my_vote:
            return None
        return True


class UserPageLabelSerializer(serializers.ModelSerializer):
    answer_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = ('id', 'name', 'intro', 'answer_count')

    def get_answer_count(self, obj):
        questions = obj.question_set.all()
        uid = self.context.get('uid')
        count = [Answer.objects.filter(question=question, author_id=uid).count() for question in questions]
        return sum(count)


class AnswerInLabelDiscussSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    vote_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    answer_id = serializers.IntegerField(source="id")
    answer_content = serializers.CharField(source="content")
    currentUserVote = serializers.SerializerMethodField(method_name="get_voted")
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "answer_id", "answer_content", "create_at", "vote_count", "comment_count", "currentUserVote", "author_info"
        )

    def get_vote_count(self, obj):
        return obj.votes.filter(value=True).count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_voted(self, obj):
        """返回None表示未投票，True表示赞成，False表示反对"""
        me = self.context["me"]  # None或者当前登录的UserProfile对象
        if not me:
            # <<<<<<< master
            return None
        my_vote = obj.votes.filter(author_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_author_info(self, obj: Answer):
        author = UserProfile.objects.get(uid=obj.author_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "autograph": author.autograph,
            "slug": author.slug,
        }
        return data
