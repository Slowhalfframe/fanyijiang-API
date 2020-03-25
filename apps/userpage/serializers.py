from rest_framework import serializers
from django.conf import settings
import json

from apps.userpage.models import (UserProfile, UserEmploymentHistory, UserEducationHistory, FollowedUser,
                                  UserLocations, UserFavorites, FollowedFavorites, FavoriteCollection)

from apps.labels.models import Label
from apps.labels.serializers import LabelCreateSerializer

from apps.questions.models import Question, QuestionFollow, Answer
from apps.questions.serializers import AnswerCreateSerializer, AnswerInLabelDiscussSerializer

from apps.articles.models import Article

from apps.ideas.models import Idea


class UserInfoSerializer(serializers.ModelSerializer):
    employment_history = serializers.SerializerMethodField()
    education_history = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('uid', 'nickname', 'avatar', 'autograph', 'gender', 'industry',
                  'employment_history', 'education_history', 'locations',
                  'description', 'slug')

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
    owner_info = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    # update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="update_time", read_only=True)

    class Meta:
        model = UserFavorites
        fields = ('id', 'title', 'status', 'content_count', 'follow_count', 'update_time', 'owner_info')

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



# class FavoritesAnswerSerializer(serializers.ModelSerializer):
#     class Meta:


class FollowsUserSerializer(serializers.ModelSerializer):
    fans_count = serializers.SerializerMethodField()  # 关注者
    articles_count = serializers.SerializerMethodField()  # 文章数
    answers_count = serializers.SerializerMethodField()  # 回答数

    class Meta:
        model = UserProfile
        fields = ('avatar', 'nickname', 'autograph', 'slug', 'uid', 'fans_count', 'articles_count', 'answers_count')

    def get_fans_count(self, obj):
        return UserProfile.objects.filter(as_fans__idol__uid=obj.uid).count()

    def get_articles_count(self, obj):
        # TODO 数据库查询
        return 0

    def get_answers_count(self, obj):
        # TODO 数据库查询
        return 0


class FavoritesContentSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    owner_info = serializers.SerializerMethodField()
    favorite_info = serializers.SerializerMethodField()


    class Meta:
        model = FavoriteCollection
        fields = ('details',)

    def get_details(self, obj):
        content_object = obj.content_object
        content_data = None
        # if isinstance(content_object, Label):
        #     content_data = LabelCreateSerializer(content_object).data

        # if isinstance(content_object, UserProfile):
        #     content_data = UserInfoSerializer(content_object).data

        if isinstance(content_object, Answer):
            content_data = UserPageAnswerSerializer(instance=content_object).data

        if isinstance(content_object, Article):
            content_data = UserPageArticleSerializer(instance=content_object).data
        # TODO 查询其他对象：文章、回答等
        return content_data

    def get_owner_info(self, obj):
        owner = obj.favorite.user
        data = {'nickname': owner.nickname, 'slug': owner.slug, 'avatar': owner.avatar}
        # 查询是否已经关注改用户
        followed = False
        if FollowedUser.objects.filter(idol__uid=owner.uid, fans__uid=self.context['uid']).exists():
            followed = True
        data['followed'] = followed
        return data

    def get_favorite_info(self, obj):
        favorite = obj.favorite
        data = FavoritesSerializer(favorite, context=self.context).data

        return data


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
    class Meta:
        model = Answer
        fields = ('question_id', 'question_title', 'top_answer')

    def get_top_answer(self, obj):
        data = AnswerInLabelDiscussSerializer(obj, context=self.context).data
        return data

    def get_question_title(self, obj):
        return obj.question.title


class UserPageArticleSerializer(serializers.ModelSerializer):

    update_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="update_at", read_only=True)
    comment_count = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'image', 'update_time', 'comment_count', 'upvote_count', 'author_info')

    def get_comment_count(self, obj):
        return obj.articlecomment_set.all().count()

    def get_upvote_count(self, obj):
        return obj.vote.filter(value=True).count()

    def get_author_info(self, obj):
        author = UserProfile.objects.filter(uid=obj.user_id).first()
        data = {
            'avatar': author.avatar,
            'nickname': author.nickname,
            'slug': author.slug,
            'autograph': author.autograph,
        }
        return data


class UserPageThinksSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", source="create_at", read_only=True)
    comment_count = serializers.SerializerMethodField()
    upvote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    avatars = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ('id', 'content', 'create_time', 'comment_count', 'upvote_count', 'author_info', 'avatars',)

    def get_comment_count(self, obj):
        return obj.ideacomment_set.all().count()

    def get_upvote_count(self, obj):
        return obj.agree.all().count()

    def get_author_info(self, obj):
        author = UserProfile.objects.filter(uid=obj.user_id).first()
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


class UserPageLabelSerializer(serializers.ModelSerializer):
    answer_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = ('id', 'name', 'intro', 'answer_count')

    def get_answer_count(self, obj):
        questions = obj.question_set.all()
        uid = self.context.get('uid')
        count = [Answer.objects.filter(question=question, user_id=uid).count() for question in questions]
        return sum(count)