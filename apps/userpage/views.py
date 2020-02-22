import json
import requests

from django.conf import settings
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.http import QueryDict

from apps.utils.api import CustomAPIView
from apps.utils.decorators import validate_serializer, validate_identity

from apps.userpage.models import (UserProfile, UserFavorites, FollowedUser, FollowedFavorites,
                                  FavoriteCollection)
from apps.userpage.serializers import (UserInfoSerializer, FavoritesSerializer, FollowsUserSerializer,
                                       FavoritesContentSerializer, UserPageQuestionSerializer, UserPageAnswerSerializer)
from apps.userpage.validators import FavoritesValidator

from apps.questions.models import Question, Answer
from apps.questions.serializers import FollowedQuestionSerializer

from apps.labels.models import Label
from apps.labels.serializers import LabelCreateSerializer


# @method_decorator(validate_token, name='dispatch')
class UserInfoAPIView(CustomAPIView):
    '''当前登录用户视图'''

    def get(self, request, user_slug):

        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            try:
                request_url = settings.USER_CENTER_GATEWAY + '/api/check_user/' + user_slug
                res = requests.get(request_url)
                if res.status_code != 200:
                    return self.error('用户中心发生错误！！！', 400)

                res_data = res.json()

                if res_data['code'] != 0:
                    return self.error('该用户不存在！', 404)

                data = res_data['data']

                user_pro_obj, status = UserProfile.objects.update_or_create(uid=data['uid'], defaults={
                    'nickname': data['nickname'], 'avatar': data['avatar'], 'autograph': data['autograph'],
                    'description': data['description'], 'slug': data['slug'], 'industry': data['industry']
                })

                user_pro_obj.location.all().delete()
                for location in data['locations']:
                    user_pro_obj.location.update_or_create(name=location['name'])

                user_pro_obj.user_education_history.all().delete()
                for education in data['education_history']:
                    user_pro_obj.user_education_history.create(**education)

                user_pro_obj.user_employment_history.all().delete()
                for employment in data['employment_history']:
                    user_pro_obj.user_professional_history.create(**employment)

                return self.success(data)

            except Exception as e:
                return self.error(e.args, 500)

        data = UserInfoSerializer(user).data
        return self.success(data)


class UcUpdateAPIView(CustomAPIView):
    '''接受统一用户中心发送过来的更新请求并更新相应内容'''

    def post(self, request):
        data = request.data.dict()
        UserProfile.objects.update_or_create(uid=data['uid'], defaults={'nickname': data['nickname'],
                                                                        'slug': data['slug'],
                                                                        'avatar': data['avatar']})
        return self.success()

    def put(self, request):
        data = request.data
        uid = data['uid']
        update_obj = data['update_obj']
        update_content = json.loads(data['update_content'])
        user_pro_obj = UserProfile.objects.get(uid=uid)

        update_dict = dict()
        if update_obj == 'locations':
            user_pro_obj.location.all().delete()
            for location in update_content['locations']:
                user_pro_obj.location.update_or_create(name=location['name'])

        elif update_obj == 'educations':
            user_pro_obj.user_education_history.all().delete()
            for education in update_content['educations']:
                user_pro_obj.user_education_history.create(**education)

        elif update_obj == 'employments':
            user_pro_obj.user_employment_history.all().delete()
            for employment in update_content['employments']:
                user_pro_obj.user_professional_history.create(**employment)

        else:
            update_dict[update_obj] = update_content[update_obj]

        user_pro_obj.__dict__.update(**update_dict)
        user_pro_obj.save()
        return self.success()


class SelfAchievementAPIView(CustomAPIView):
    '''个人成就'''

    def get(self, request):
        # 全部文章被赞同的数量 + 全部想法被赞同的数量 + 全部回答被赞同的数量
        pass

        # 全部文章被收藏的数量 + 全部回答被收藏的数量 + 全部想法被赞同的数量
        pass

        # 全部回答被喜欢的数量
        pass


class FollowingUserAPIView(CustomAPIView):
    '''关注该用户'''

    @validate_identity  #TODO 这种方式响应时间较长，怎么处理比较好？
    def get(self, request, user_slug):
        '''查看是否已经关注该用户'''
        uid = request._request.uid
        me = UserProfile.objects.filter(uid=uid).first()
        idol = UserProfile.objects.filter(slug=user_slug).first()
        data = {'followed': False}
        if FollowedUser.objects.filter(fans=me, idol=idol).exists():
            data['followed'] = True
        return self.success(data)

    @validate_identity
    def post(self, request, user_slug):
        ''''''
        uid = request._request.uid
        idol_user = UserProfile.objects.filter(slug=user_slug).first()
        if not idol_user:
            return self.error('error', 404)
        if idol_user.uid == uid:
            return self.error('不能关注自己', 400)
        if FollowedUser.objects.filter(fans_id=uid, idol=idol_user).exists():
            return self.error('不能重复关注', 400)
        FollowedUser.objects.create(fans_id=uid, idol=idol_user)
        return self.success()

    # 取关该用户
    @validate_identity
    def delete(self, request, user_slug):
        uid = request._request.uid
        idol_user = UserProfile.objects.filter(slug=user_slug).first()
        if idol_user:
            FollowedUser.objects.filter(fans_id=uid, idol=idol_user).delete()
            return self.success()
        return self.error('error', 400)


class FollowingFavoritesAPIView(CustomAPIView):
    '''关注收藏夹'''

    @validate_identity
    def post(self, request, pk):
        # uid = request.data.get('uid')
        uid = request._request.uid
        try:
            user = UserProfile.objects.get(uid=uid)
            fa = UserFavorites.objects.get(pk=pk)
            if fa.user_id == uid:
                return self.error('不能关注自己的收藏夹', 400)
            FollowedFavorites.objects.create(user=user, fa_id=pk)

        except UserFavorites.DoesNotExist:
            return self.error('收藏夹不存在', 404)
        except UserProfile.DoesNotExist:
            return self.error('用户不存在', 404)
        except Exception as e:
            return self.error('未知错误', 500)
        return self.success()

    # 取消关注
    @validate_identity
    def delete(self, request, pk):
        # uid = request.data.get('uid')
        uid = request._request.uid
        try:
            user = UserProfile.objects.get(uid=uid)
            fa = UserFavorites.objects.get(pk=pk)
            FollowedFavorites.objects.filter(user=user, fa=fa).delete()

        except UserFavorites.DoesNotExist:
            return self.error('收藏夹不存在', 404)
        except UserProfile.DoesNotExist:
            return self.error('用户不存在', 404)
        except Exception as e:
            return self.error('未知错误', 500)
        return self.success()


class FavoritesListAPIView(CustomAPIView):
    def get(self, request, user_slug):
        '''用户列表页收藏夹列表'''
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # 获取该用户下所有收藏夹
        favorites = user.favorites.all()
        data = self.paginate_data(request, favorites, FavoritesSerializer)
        return self.success(data)


class QuestionListAPIView(CustomAPIView):
    '''发起的提问列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        questions = Question.objects.filter(user_id=user.id)
        data = self.paginate_data(request, questions, UserPageQuestionSerializer)
        return self.success(data)


class AnswerListAPIView(CustomAPIView):
    '''回答列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        answers = Answer.objects.filter(user_id=user.id)
        data = self.paginate_data(request, answers, UserPageAnswerSerializer)
        return self.success(data)


class ThinkListAPIView(CustomAPIView):
    '''想法列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库

        data = {'results': [], 'total': 0}
        return self.success(data)


class ArticleListAPIView(CustomAPIView):
    '''发表文章列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库

        data = {'results': [], 'total': 0}
        return self.success(data)


class SelfFavoritesAPIView(CustomAPIView):
    '''用户创建或者修改收藏夹操作'''

    @validate_serializer(FavoritesValidator)
    def post(self, request):
        '''创建收藏夹'''
        data = request.data
        user = UserProfile.objects.filter(uid=data['uid']).first()

        if not user:
            return self.error('该用户不存在', 404)

        if UserFavorites.objects.filter(title=data['title']).exists():
            return self.error('该收藏夹已经创建过了', 400)
        UserFavorites.objects.create(user=user, title=data['title'], content=data['content'], status=data['status'])

        return self.success()

    @validate_serializer(FavoritesValidator)
    def put(self, request):
        '''修改收藏夹'''
        data = request.data
        user = UserProfile.objects.filter(uid=data['uid']).first()
        if not user:
            return self.error('该用户不存在', 404)

        fa = UserFavorites.objects.filter(pk=data['fa_id']).first()
        if not fa:
            return self.error('没有该收藏夹', 404)

        fa.title = data['title']
        fa.content = data['content']
        fa.status = data['status']
        fa.save()

        return self.success()

    def delete(self, request):
        '''删除收藏夹'''
        data = QueryDict(request.body)
        user = UserProfile.objects.filter(uid=data['uid']).first()
        if not user:
            return self.error('该用户不存在', 404)

        fa = UserFavorites.objects.filter(pk=data['fa_id']).first()
        if not fa:
            return self.error('没有该收藏夹', 404)
        UserFavorites.objects.filter(user=user, pk=data['fa_id']).delete()
        return self.success()


class FollowedFavoritesAPIView(CustomAPIView):
    '''关注的收藏夹'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('用户不存在', 404)

        followed_fas = UserFavorites.objects.filter(followed_fa__user=user)
        data = self.paginate_data(request, followed_fas, FavoritesSerializer)
        return self.success(data)


class FollowedUserAPIView(CustomAPIView):
    '''关注的用户与被关注的用户列表'''

    @validate_identity
    def get(self, request, user_slug):
        '''获取该用户的关注者和被关注者'''
        uid = request._request.uid
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            return self.error('用户不存在', 404)

        include = request.GET.get('include')

        fans = FollowedUser.objects.filter(idol=user)
        idol = FollowedUser.objects.filter(fans=user)

        fans_nums = fans.count()
        idol_nums = idol.count()

        data = {'fans_nums': fans_nums, "idol_nums": idol_nums}

        if include not in ['fans', 'idol']:
            return self.success(data)

        # 获取关注该用户的人
        if include == 'fans':
            fans = UserProfile.objects.filter(as_fans__idol__slug=user_slug)
            data = self.paginate_data(request, fans, FollowsUserSerializer)

        # 获取该用户关注的人
        if include == 'idol':
            idol = UserProfile.objects.filter(as_idol__fans__slug=user_slug)
            data = self.paginate_data(request, idol, FollowsUserSerializer)

        # 处理当前登录也关注所查看该用户关注的人
        results = data['results']
        for r in results:
            r['is_idol'] = False
            if UserProfile.objects.filter(as_idol__fans__uid=uid, slug=r['slug']).exists():
                r['is_idol'] = True
        return self.success(data)


class FollowedLabelAPIView(CustomAPIView):
    '''关注的标签'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('用户不存在', 404)

        # TODO 查询标签关注表
        follows = Label.objects.filter(labelfollow__user_id=user.id)
        data = self.paginate_data(request, follows, LabelCreateSerializer)
        return self.success(data)


class FollowedQuestionsAPIView(CustomAPIView):
    '''关注的问题'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('用户不存在', 404)

        # TODO 查询问题关注表
        questions = Question.objects.filter(questionfollow__user_id=user.id)
        data = self.paginate_data(request, questions, FollowedQuestionSerializer)
        return self.success(data)


class FavoritesContentAPIView(CustomAPIView):
    '''收藏夹内的内容'''

    def get(self, request, pk):
        fa = UserFavorites.objects.filter(pk=pk).first()

        if not fa:
            return self.error('找不到该收藏夹', 404)

        fa_content = fa.favorite_collect.all()
        data = self.paginate_data(request, fa_content, FavoritesContentSerializer)
        return self.success(data)

    def post(self, request, pk):
        '''添加收藏夹内容'''
        fa = UserFavorites.objects.filter(pk=pk).first()
        if not fa:
            return self.error('请选择正确的收藏夹', 400)
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        if content_type == 'answer':
            answer = Answer.objects.filter(pk=object_id).first()
            answer.collect.update_or_create(favorite=fa)
        if content_type == 'article':
            pass

        return self.success()

    def delete(self, request, pk):
        fa = UserFavorites.objects.filter(pk=pk).first()
        if not fa:
            return self.error('请选择正确的收藏夹', 400)
        delete = QueryDict(request.body)
        content_type = delete.get('content_type')
        object_id = delete.get('object_id')

        if content_type == 'answer':
            answer = Answer.objects.filter(pk=object_id).first()
            answer.collect.get(favorite=fa).delete()

        if content_type == 'article':
            pass

        return self.success()


class CollectedAPIView(CustomAPIView):
    '''获取当前回答已收藏的收藏夹'''

    def get(self, request, user_slug, content_type, object_id):
        favorites = UserFavorites.objects.filter(user__slug=user_slug)
        data_list = [{'title': fa.title, 'id': fa.id, 'content': fa.favorite_collect.all()} for fa in favorites]
        instance = None
        if content_type == 'answer':
            instance = Answer.objects.filter(pk=object_id).first()
        if content_type == 'article':
            pass

        for data in data_list:
            # 检查是否已收藏
            data['collected'] = False
            data['content_count'] = len(data['content'])
            instance_list = [obj.content_object for obj in data['content']]
            if instance in instance_list:
                data['collected'] = True
            data.pop('content')
        return self.success(data_list)