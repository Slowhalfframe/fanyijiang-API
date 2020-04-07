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
                                       FavoritesContentSerializer, UserPageQuestionSerializer, UserPageAnswerSerializer,
                                       UserPageArticleSerializer, UserPageThinksSerializer, UserPageLabelSerializer,
                                       ContentFavoritesSerializer)
from apps.userpage.validators import FavoritesValidator

from apps.questions.models import Question, Answer, QuestionFollow

from apps.articles.models import Article

from apps.labels.models import Label, LabelFollow

from apps.taskapp.tasks import notification_handler

from apps.pins.models import Idea

from apps.creator.views import ArticleVoteStatistics, ArticleCollectStatistics, AnswerVoteStatistics, \
    AnswerCollectStatistics, ThinkVoteStatistics, ThinkCollectStatistics


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

                user, status = UserProfile.objects.update_or_create(uid=data['uid'], defaults={
                    'nickname': data['nickname'], 'avatar': data['avatar'], 'autograph': data['autograph'],
                    'description': data['description'], 'slug': data['slug'], 'industry': data['industry']
                })
                user.location.all().delete()

                try:
                    locations = data['locations']
                    for location in locations:
                        user.location.update_or_create(name=location['name'])

                    user.user_education_history.all().delete()
                    education_history = data['education_history']
                    for education in education_history:
                        user.user_education_history.create(**education)

                    user.user_employment_history.all().delete()
                    employment_history = data['employment_history']
                    for employment in employment_history:
                        user.user_employment_history.create(**employment)
                except:
                    locations = json.loads(data['locations'])
                    for location in locations:
                        user.location.update_or_create(name=location['name'])

                    user.user_education_history.all().delete()
                    education_history = json.loads(data['education_history'])
                    for education in education_history:
                        user.user_education_history.create(**education)

                    user.user_employment_history.all().delete()
                    employment_history = json.loads(data['employment_history'])
                    for employment in employment_history:
                        user.user_employment_history.create(**employment)

            except Exception as e:
                return self.error(e.args, 500)

        data = UserInfoSerializer(user).data
        create_content_nums = {
            'question_count': Question.objects.filter(author_id=user.uid).count(),
            'answer_count': Answer.objects.filter(author_id=user.uid).count(),
            'article_count': Article.objects.filter(author_id=user.uid, status='published', is_deleted=False).count(),
            'think_count': Idea.objects.filter(author_id=user.uid).count(),
            'collect_count': user.favorites.all().count(),
        }
        data['create_content_nums'] = create_content_nums

        # 个人成就
        # 全部文章被赞同的数量 + 全部想法被赞同的数量 + 全部回答被赞同的数量
        article_upvotes = ArticleVoteStatistics(user).get_total_upvote_nums() or 0
        answer_upvotes = AnswerVoteStatistics(user).get_total_upvote_nums() or 0
        think_upvotes = ThinkVoteStatistics(user).get_total_upvote_nums() or 0
        upvotes = article_upvotes + answer_upvotes + think_upvotes

        # 全部文章被收藏的数量 + 全部回答被收藏的数量 + 全部想法被赞同的数量

        article_collect = ArticleCollectStatistics(user).get_total_collect_nums()
        answer_collect = ArticleCollectStatistics(user).get_total_collect_nums()
        think_collect = ThinkCollectStatistics(user).get_total_collect_nums()
        collect_count = article_collect + answer_collect + think_collect


        self_achievement = {'upvote_count': upvotes, 'collect_count': collect_count}
        data['self_achievement'] = self_achievement

        # 关注的人
        fans = FollowedUser.objects.filter(idol=user)
        idol = FollowedUser.objects.filter(fans=user)

        fans_nums = fans.count()
        idol_nums = idol.count()

        fans_and_idols = {'fans_nums': fans_nums, "idol_nums": idol_nums}
        data['fans_and_idols'] = fans_and_idols

        # 关注的信息
        # 标签
        followed_label_count = LabelFollow.objects.filter(user_id=user.uid).count()
        followed_question_count = QuestionFollow.objects.filter(user_id=user.uid).count()
        followed_favorites_count = FollowedFavorites.objects.filter(user=user).count()

        followed_content = {
            'followed_label_count': followed_label_count,
            'followed_question_count': followed_question_count,
            'followed_favorites_count': followed_favorites_count,
        }

        data['followed_content'] = followed_content
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
            locations = json.loads(update_content['locations'])
            for location in locations:
                user_pro_obj.location.update_or_create(**location)

        elif update_obj == 'educations':
            user_pro_obj.user_education_history.all().delete()
            educations = json.loads(update_content['educations'])
            for education in educations:
                user_pro_obj.user_education_history.create(**education)

        elif update_obj == 'employments':
            user_pro_obj.user_employment_history.all().delete()
            employments = json.loads(update_content['employments'])
            for employment in employments:
                user_pro_obj.user_employment_history.create(**employment)

        else:
            update_dict[update_obj] = update_content[update_obj]

        user_pro_obj.__dict__.update(**update_dict)
        user_pro_obj.save()
        return self.success()


class UserPageImagePUTAPIView(CustomAPIView):
    '''更新个人主页图片'''
    @validate_identity
    def put(self, request):
        user_id = request._request.uid
        user = UserProfile.objects.get(pk=user_id)
        if not user:
            return self.error('error', 401)

        page_image = request.data.get('page_image', None)
        if page_image:
            user.page_image = page_image
            user.save()
            return self.success('success')
        return self.error('无效的数据', 100003)


class HoverUserInfoAPIView(CustomAPIView):
    '''但鼠标放在用户头像上时，显示用户部分信息'''

    # @validate_identity
    def get(self, request, user_slug):
        uid = self.get_user_profile(request).uid if self.get_user_profile(request) else None
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            return self.error('error', 404)
        user_info = {'avatar': user.avatar, 'nickname': user.nickname, 'autograph': user.autograph,
                     'slug': user.slug
                     }
        employment = {
            'company': user.user_employment_history.first().company if user.user_employment_history.first() else None,
            'position': user.user_employment_history.first().position if user.user_employment_history.first() else None,
            }
        has_followed = True if FollowedUser.objects.filter(fans__uid=uid, idol__uid=user.uid).exists() else False
        create_count = {
            'answer_count': Answer.objects.filter(author_id=user.uid).count(),
            'article_count': Article.objects.filter(author_id=user.uid, status='published', is_deleted=False).count(),

            'fans_count': FollowedUser.objects.filter(idol=user).count(),
            'has_followed': has_followed
        }

        data = {
            'user_info': user_info,
            'employment': employment,
            'create_count': create_count,
        }
        return self.success(data)


class HoverLabelInfoAPIView(CustomAPIView):
    '''但鼠标放在用户头像上时，显示用户部分信息'''

    def get(self, request, pk):
        label = Label.objects.filter(pk=pk).first()
        if not label:
            return self.error('not found', 404)
        user = self.get_user_profile(request)
        data = {
            'id': label.id,
            'name': label.name,
            'intro': label.intro,
            'question_count': Question.objects.filter(labels=label).count(),
            'followed_user_count': LabelFollow.objects.filter(label=label).count(),
            'is_followed': LabelFollow.objects.filter(label=label, user_id=user.uid).exists() if user else False
        }
        return self.success(data)


# class SelfAchievementAPIView(CustomAPIView):
#     '''个人成就'''
#
#     def get(self, request, user_slug):
#         user = UserProfile.objects.filter(slug=user_slug).first()
#         if not user:
#             return self.error('error', 404)
#
#         # 全部文章被赞同的数量 + 全部想法被赞同的数量 + 全部回答被赞同的数量
#         article_upvotes = ArticleVoteStatistics(user).get_total_upvote_nums() or 0
#         answer_upvotes = AnswerVoteStatistics(user).get_total_upvote_nums() or 0
#         think_upvotes = ThinkVoteStatistics(user).get_total_upvote_nums() or 0
#         upvotes = article_upvotes + answer_upvotes + think_upvotes
#
#         # 全部文章被收藏的数量 + 全部回答被收藏的数量 + 全部想法被赞同的数量
#
#         article_collect = ArticleCollectStatistics(user).get_total_collect_nums()
#         answer_collect = ArticleCollectStatistics(user).get_total_collect_nums()
#         collect_count = article_collect + answer_collect
#
#         data = {'upvote_count': upvotes, 'collect_count': collect_count}
#         return self.success(data)


class FollowingUserAPIView(CustomAPIView):
    '''关注该用户'''

    # @validate_identity  # TODO 这种方式响应时间较长，怎么处理比较好？
    def get(self, request, user_slug):
        '''查看是否已经关注该用户'''
        user = self.get_user_profile(request)
        # uid = request._request.uid
        data = dict()
        data['followed'] = False
        if not user:
            return self.success(data)
        me = UserProfile.objects.filter(uid=user.uid).first()
        idol = UserProfile.objects.filter(slug=user_slug).first()
        if user and FollowedUser.objects.filter(fans=me, idol=idol).exists():
            data['followed'] = True
        return self.success(data)

    @validate_identity
    def post(self, request, user_slug):
        ''''''
        uid = request._request.uid
        print(uid, '用户ID')
        idol_user = UserProfile.objects.filter(slug=user_slug).first()
        if not idol_user:
            return self.error('error', 404)
        if idol_user.uid == uid:
            return self.error('不能关注自己', 400)
        if FollowedUser.objects.filter(fans_id=uid, idol=idol_user).exists():
            return self.error('不能重复关注', 400)
        fans = UserProfile.objects.get(uid=uid)
        FollowedUser.objects.create(fans=fans, idol=idol_user)

        # TODO 触发消息通知
        notification_handler.delay(uid, idol_user.uid, 'O', idol_user.uid)
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
            if fa.user == user:
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
    @validate_identity
    def get(self, request, user_slug):
        uid = request._request.uid
        '''用户列表页收藏夹列表'''
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            user = self.get_user_profile(request)
            if not user:
                return self.error('该用户不存在', 404)
        if user.uid == uid:
            # 获取该用户下所有收藏夹
            favorites = user.favorites.all()
        else:
            favorites = user.favorites.filter(status='public')
        data = self.paginate_data(request, favorites, FavoritesSerializer, {'uid': user.uid})
        return self.success(data)


class QuestionListAPIView(CustomAPIView):
    '''发起的提问列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        questions = Question.objects.filter(author_id=user.uid)
        data = self.paginate_data(request, questions, UserPageQuestionSerializer)
        return self.success(data)


class AnswerListAPIView(CustomAPIView):
    '''回答列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        answers = Answer.objects.filter(author_id=user.uid)
        data = self.paginate_data(request, answers, UserPageAnswerSerializer, serializer_context={'me': user})
        return self.success(data)


class ThinkListAPIView(CustomAPIView):
    '''想法列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        ideas = Idea.objects.filter(author_id=user.uid)
        data = self.paginate_data(request, ideas, UserPageThinksSerializer, {'me': user})
        return self.success(data)


class ArticleListAPIView(CustomAPIView):
    '''发表文章列表'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        # TODO 查询相关数据库
        articles = Article.objects.filter(author_id=user.uid, status='published', is_deleted=False)

        data = self.paginate_data(request, articles, UserPageArticleSerializer, {'me': user})
        # data = {'results': [], 'total': 0}
        return self.success(data)


class SelfFavoritesAPIView(CustomAPIView):
    '''用户创建或者修改收藏夹操作'''

    @validate_identity
    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            return self.error('该用户不存在', 404)
        fa_id = request.GET.get('fa_id')
        fa = UserFavorites.objects.filter(pk=fa_id, user=user).first()
        if not fa:
            return self.error('该收藏夹不存在！', 10089)
        data = ContentFavoritesSerializer(fa, context={'uid': user.uid}).data
        return self.success(data)

    @validate_serializer(FavoritesValidator)
    def post(self, request, user_slug):
        '''创建收藏夹'''
        data = request.data
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)

        if UserFavorites.objects.filter(title=data['title']).exists():
            return self.error('该收藏夹已经创建过了', 400)
        UserFavorites.objects.create(user=user, title=data['title'], intro=data['content'], status=data['status'])

        return self.success()

    @validate_serializer(FavoritesValidator)
    @validate_identity
    def put(self, request, user_slug):
        '''修改收藏夹'''
        data = request.data
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            return self.error('该用户不存在', 404)
        if user.uid != request._request.uid:
            return self.error('只能修改自己的收藏夹', 404)
        fa = UserFavorites.objects.filter(pk=data['fa_id']).first()
        if not fa:
            return self.error('没有该收藏夹', 404)

        fa.title = data['title']
        fa.intro = data['content']
        fa.status = data['status']
        fa.save()

        return self.success()

    @validate_identity
    def delete(self, request, user_slug):
        '''删除收藏夹'''
        data = request.query_params.dict()
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('该用户不存在', 404)
        if user.uid != request._request.uid:
            return self.error('没有权限删除', 404)

        fa = UserFavorites.objects.filter(pk=data.get('fa_id')).first()
        if not fa:
            return self.error('没有该收藏夹', 404)
        UserFavorites.objects.filter(user=user, pk=data.get('fa_id')).delete()
        return self.success()


class FollowedFavoritesAPIView(CustomAPIView):
    '''关注的收藏夹'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            user = self.get_user_profile(request)
            if not user:
                return self.error('用户不存在', 404)

        followed_fas = UserFavorites.objects.filter(followed_fa__user=user)
        data = self.paginate_data(request, followed_fas, FavoritesSerializer, {"uid": user.uid})
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


class FollowedUserCountAPIView(CustomAPIView):
    '''关注的用户与被关注的用户列表'''

    def get(self, request, user_slug):
        '''获取该用户的关注者和被关注者'''
        user = UserProfile.objects.filter(slug=user_slug).first()
        if not user:
            return self.error('用户不存在', 404)

        fans = FollowedUser.objects.filter(idol=user)
        idol = FollowedUser.objects.filter(fans=user)

        fans_nums = fans.count()
        idol_nums = idol.count()

        data = {'fans_nums': fans_nums, "idol_nums": idol_nums}

        return self.success(data)


class FollowedLabelAPIView(CustomAPIView):
    '''关注的标签'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('用户不存在', 404)

        # TODO 查询标签关注表
        follows = Label.objects.filter(labelfollow__author_id=user.uid)
        serializer_context = {'uid': user.uid}
        data = self.paginate_data(request, follows, UserPageLabelSerializer, serializer_context=serializer_context)
        return self.success(data)


class FollowedQuestionsAPIView(CustomAPIView):
    '''关注的问题'''

    def get(self, request, user_slug):
        user = UserProfile.objects.filter(slug=user_slug).first()

        if not user:
            return self.error('用户不存在', 404)

        # TODO 查询问题关注表
        questions = Question.objects.filter(questionfollow__user_id=user.uid)
        data = self.paginate_data(request, questions, UserPageQuestionSerializer)
        return self.success(data)


class FavoritesContentAPIView(CustomAPIView):
    '''收藏夹内的内容'''
    @validate_identity
    def get(self, request, user_slug, pk):
        fa = UserFavorites.objects.filter(pk=pk).first()

        if not fa:
            return self.error('找不到该收藏夹', 404)

        fa_content = fa.favorite_collect.all()
        data = dict()
        content_data = self.paginate_data(request, fa_content, FavoritesContentSerializer, {'me': fa.user})

        owner = fa.user
        owner_info = {'nickname': owner.nickname, 'slug': owner.slug, 'avatar': owner.avatar, 'autograph': owner.autograph}
        # 查询是否已经关注改用户
        followed = False
        if FollowedUser.objects.filter(idol__uid=owner.uid, fans__uid=request._request.uid).exists():
            followed = True
        owner_info['followed'] = followed
        owner_info['is_me'] = False
        if fa.user.uid == request._request.uid:
            owner_info['is_me'] = True
        favorite_info = ContentFavoritesSerializer(fa, context={'uid':request._request.uid}).data
        data['content_data'] = content_data
        data['owner_info'] = owner_info
        data['favorite_info'] = favorite_info
        fa.save()
        return self.success(data)

    def post(self, request, user_slug, pk):
        '''添加收藏夹内容'''
        fa = UserFavorites.objects.filter(pk=pk).first()
        if not fa:
            return self.error('请选择正确的收藏夹', 400)
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')

        model_mappings = {'answer': Answer, 'article': Article, 'think': Idea}
        if content_type not in model_mappings:
            return self.error('未知的数据类型', 404)
        which_model = model_mappings['content_type']

        # if content_type == 'answer':
        #     answer = Answer.objects.filter(pk=object_id).first()
        #     answer.collect.update_or_create(favorite=fa)
        if content_type == 'article':
            article = Article.objects.filter(pk=object_id, status='published', is_deleted=False).first()
            article.collect.update_or_create(favorite=fa)
        else:
            instance = which_model.objects.filter(pk=object_id).first()
            instance.collect.update_or_create(favorite=fa)
        # if content_type == 'think':
        #     think = Idea.objects.filter(pk=object_id).first()
        #     think.collect.update_or_create(favorite=fa)
        fa.save()
        return self.success()

    def delete(self, request, user_slug, pk):
        fa = UserFavorites.objects.filter(pk=pk).first()
        if not fa:
            return self.error('请选择正确的收藏夹', 400)
        delete = request.query_params.dict()
        content_type = delete.get('content_type')
        object_id = delete.get('object_id')

        model_mappings = {'answer': Answer, 'article': Article, 'think': Idea}
        if content_type not in model_mappings:
            return self.error('未知的数据类型', 404)
        which_model = model_mappings['content_type']

        # if content_type == 'answer':
        #     answer = Answer.objects.filter().first()
        #     answer.collect.get(favorite=fa).delete()
        if content_type == 'article':
            article = Article.objects.filter(pk=object_id, status='published', is_deleted=False).first()
            article.collect.get(favorite=fa).delete()
        else:
            instance = which_model.objects.filter(pk=object_id).first()
            instance.collect.get(favorite=fa).delete()
        # if content_type == 'think':
        #     think = Idea.objects.filter(pk=object_id).first()
        #     think.collect.get(favorite=fa).delete()
        fa.save()
        return self.success()


class CollectedAPIView(CustomAPIView):
    '''获取当前回答已收藏的收藏夹'''

    @validate_identity
    def get(self, request, user_slug, content_type, object_id):
        favorites = UserFavorites.objects.filter(user__slug=user_slug)
        data_list = [{'title': fa.title, 'id': fa.id, 'content': fa.favorite_collect.all()} for fa in favorites]
        instance = None
        if content_type == 'answer':
            instance = Answer.objects.filter(pk=object_id).first()
        if content_type == 'article':
            instance = Article.objects.filter(pk=object_id, status='published', is_deleted=False).first()
        if content_type == 'think':
            instance = Idea.objects.filter(pk=object_id).first()
        for data in data_list:
            # 检查是否已收藏
            data['collected'] = False
            data['content_count'] = len(data['content'])
            instance_list = [obj.content_object for obj in data['content']]
            if instance in instance_list:
                data['collected'] = True
            data.pop('content')
        return self.success(data_list)
