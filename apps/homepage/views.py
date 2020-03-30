import random, math, datetime

from apps.utils.api import CustomAPIView
from apps.questions.models import Question, Answer, QuestionFollow, ACVote

from apps.labels.models import Label, LabelFollow

from apps.articles.models import Article, ArticleVote

from apps.userpage.models import UserFavorites, UserProfile


class BaseCreateContent(object):
    def __init__(self, user, offset, limit):
        self.user = user
        self.offset = int(offset)
        self.limit = int(limit)

    def get_labels(self, content):
        '''获取某一个内容的所有标签'''
        if isinstance(content, Question) or isinstance(content, Article):
            labels = content.labels.all()
        else:
            labels = []
        return labels

    def get_label_hash(self, content_list):
        '''根据标签列表生成标签权重'''
        label_hash = dict()
        for content in content_list:
            labels = self.get_labels(content)
            for label in labels:
                if label.id not in label_hash:
                    label_hash[label.id] = 1
                else:
                    label_hash[label.id] += 1
        return label_hash


class UserCreateArticle(BaseCreateContent):
    '''创作的内容，文章'''

    def get_user_article(self):
        '''用户创作的文章'''
        articles = [a for a in Article.objects.filter(user_id=self.user.uid).order_by('-create_at')[
                               self.offset:self.offset + self.limit]]
        return articles

    def get_article_label_hash(self):
        '''根据创建的文章生成标签权重字典'''
        articles = self.get_user_article()
        label_hash = self.get_label_hash(articles)
        return label_hash

    def get_user_answer_question(self):
        '''获取用户发表回答的问题'''
        questions = [a.question for a in Answer.objects.filter(user_id=self.user.uid).order_by('-create_at')[
                                         self.offset:self.offset + self.limit]]
        return questions

    def get_answer_label_hash(self):
        '''根据问题生成标签权重字典'''
        questions = self.get_user_answer_question()
        label_hash = self.get_label_hash(questions)
        return label_hash


class UserCreateCollect(BaseCreateContent):
    '''参与度：收藏，点赞'''

    def get_user_favorites(self):
        '''获取用户的收藏夹'''
        favorites = [a for a in UserFavorites.objects.filter(user_id=self.user.uid)[
                                self.offset:self.offset + self.limit]]
        return favorites

    def get_favorites_content(self):
        '''获取收藏夹内的内容列表'''
        favorites = self.get_user_favorites()
        content_list = list()
        for favorite in favorites:
            contents = favorite.favorite_collect.all()[self.offset:self.offset + self.limit]
            for content in contents:
                content_list.append(content.content_object)
        return content_list

    def get_collect_label_hash(self):
        '''根据收藏夹的内容生成标签字典'''
        contents = self.get_favorites_content()
        label_hash = self.get_label_hash(contents)
        return label_hash

    def get_recent_vote_content(self):
        '''获取最近点赞的内容'''
        ac_votes = ACVote.objects.filter(user_id=self.user.uid)[self.offset:self.offset + self.limit]
        contents = [v.content_object for v in ac_votes]
        article_vote = ArticleVote.objects.filter(user_id=self.user.uid)[self.offset:self.offset + self.limit]
        article_contents = [v.content_object for v in article_vote]
        contents.extend(article_contents)
        return contents

    def get_vote_label_hash(self):
        '''根据点赞的内容生成标签字典'''
        contents = self.get_recent_vote_content()
        label_hash = self.get_label_hash(contents)
        return label_hash


class GetFinalLabel(UserCreateArticle, UserCreateCollect):
    def get_labels_dict(self):
        '''根据获取所有标签权重列表生成新的字典'''
        label_dict_list = self.get_labels_dict_list()
        followed_labels_dict = self.merge_dict(label_dict_list)
        return followed_labels_dict

    def get_labels_dict_list(self):
        '''获取所有标签权重列表'''
        label_dict_list = list()
        label_dict_list.append(self.get_user_followed_label_dict())
        label_dict_list.append(self.get_article_label_hash())
        label_dict_list.append(self.get_collect_label_hash())
        label_dict_list.append(self.get_answer_label_hash())
        label_dict_list.append(self.get_vote_label_hash())
        return label_dict_list

    def get_user_followed_label_dict(self):
        '''获取用户关注的标签字典'''
        followed_labels_dict = dict()
        followed_labels = Label.objects.filter(labelfollow__user_id=self.user.uid)[self.offset:self.offset + self.limit]
        for f in followed_labels:
            followed_labels_dict[f.id] = 1
        return followed_labels_dict

    def get_user_no_followed_label(self):
        '''获取用户未关注的标签列表'''
        labels = Label.objects.exclude(labelfollow__user_id=self.user.uid)[self.offset:self.offset + self.limit]
        ls = [l for l in labels]
        return ls

    def merge_dict(self, label_dict_list):
        '''比较两个字典，相同的key相加，不同的key合并'''
        if len(label_dict_list) == 1:
            return label_dict_list[0]
        else:
            dict1 = label_dict_list[0]
            dict2 = label_dict_list[1]
            for k, v in dict1.items():
                if k in dict2.keys():
                    dict2[k] += v
                else:
                    dict2[k] = v
            new_dict = dict2
            label_dict_list.remove(dict1)
            label_dict_list.remove(dict2)
            label_dict_list.insert(0, new_dict)
            return self.merge_dict(label_dict_list)


class InLabelContent(BaseCreateContent):
    '''根据生成权重最高的标签，获取相应的推荐内容'''

    def get_label_question(self, label):
        '''问题'''
        questions = [q for q in
                     label.question_set.all().order_by('-create_at')[self.offset:self.offset + self.limit]]
        return questions

    def get_lable_article(self, label):
        '''文章'''
        articles = [a for a in label.article_set.filter(status='published', is_deleted=False).exclude(
            user_id=self.user.uid).order_by('-create_at')[self.offset:self.offset + self.limit]]
        return articles

    def get_question_answer(self, question):
        '''回答'''
        answer = [a for a in question.answer_set.exclude(user_id=self.user.uid).order_by('-create_at')[
                             self.offset:self.offset + self.limit]]
        return answer

    def get_content_list(self, label):
        '''整合内容：文章30%，回答50%'''
        # content_list = self.get_lable_article(label)
        random_length = math.ceil(self.limit * 0.3)
        data_list = self.get_lable_article(label)
        content_list = random.sample(data_list, random_length) if len(data_list) > random_length else data_list
        for questoin in self.get_label_question(label):
            random_length = self.limit * 0.5
            answer_list = self.get_question_answer(questoin)
            answers = random.sample(answer_list, random_length) if len(answer_list) > random_length else answer_list
            content_list.extend(answers)
        return content_list

    def get_finally_data(self):
        '''生成最终返回数据
            由用户行为产生的数据占比80%，其他内容为20%
        '''
        finally_label = GetFinalLabel(self.user, self.offset, self.limit)
        finally_label_dict = finally_label.get_labels_dict()
        no_labels = finally_label.get_user_no_followed_label()

        data_list = list()
        while len(data_list) <= self.limit:
            if len(finally_label_dict) > 1 and len(data_list) < self.limit:
                max_label_id = max(finally_label_dict, key=finally_label_dict.get)
                label = Label.objects.get(pk=max_label_id)
                data_list.extend(self.get_content_list(label))
                finally_label_dict.pop(max_label_id)

            if len(finally_label_dict) <= 1 and len(data_list) < self.limit or len(data_list) > self.limit * 0.8:
                # 从其他标签下获取一个内容
                print(no_labels)
                if not len(no_labels):
                    break
                no_label = random.choice(no_labels)
                no_labels.remove(no_label)
                data_list.extend(self.get_content_list(no_label))
            data_list = list(set(data_list))
        return data_list


from apps.userpage.serializers import UserPageArticleSerializer, UserPageAnswerSerializer


# Create your views here.
class HomePageRecommendAPIView(CustomAPIView):

    def get(self, request):
        user = self.get_user_profile(request)
        if not user:
            return self.error('error', 401)
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        data_list = InLabelContent(user, offset, limit).get_finally_data()
        data = list()
        for obj in data_list:
            if isinstance(obj, Article):
                content_data = UserPageArticleSerializer(obj, context={'me': user}).data
            if isinstance(obj, Answer):
                content_data = UserPageAnswerSerializer(obj, context={'me': user}).data
            data.append(content_data)
        return self.success(data)


class HomePageFollowContentAPIView(CustomAPIView):

    def get(self, request):
        user = self.get_user_profile(request)
        if not user:
            return self.error('error', 401)
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        idol_users = UserProfile.objects.filter(as_idol__fans=user)[offset:offset + limit]
        data_list = list()
        for idol in idol_users:
            answer = Answer.objects.filter(user_id=idol.uid).order_by('-create_at')
            answer_data = self.paginate_data(request, answer, UserPageAnswerSerializer, serializer_context={'me': idol})
            data_list.extend(answer_data['results'])
            articles = Article.objects.filter(user_id=idol.uid).order_by('-update_at', '-create_at')
            article_data = self.paginate_data(request, articles, UserPageArticleSerializer,
                                              serializer_context={'me': idol})
            data_list.extend(article_data['results'])

        data = sorted(data_list, key=lambda x: x['update_time'], reverse=True)
        return self.success(data)


class WaitAnswerAPIView(CustomAPIView):
    def get(self, request):
        from apps.creator.views import RecommendQuestion
        user = self.get_user_profile(request)
        if not user:
            return self.error('error', 401)

        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 20)
        recommend = RecommendQuestion(user, offset, limit)
        questions = recommend.get_finally_question()
        data = recommend.get_json_data(questions)
        return self.success(data)


class HomePageCreatorAPIView(CustomAPIView):
    def get(self, request):
        from apps.creator.views import TotalNums
        user = self.get_user_profile(request)
        if not user:
            return self.error('error', 401)

        # 阅读量
        total_instance = TotalNums(user)
        # 昨日总阅读量
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_str = datetime.date.strftime(yesterday, '%Y%m%d')
        ysd_read_nums = total_instance.get_date_total_nums(yesterday_str)
        ysd_upvote = total_instance.get_date_total_votes(yesterday_str)
        data = {'ysd_read_nums': ysd_read_nums, 'ysd_upvote': ysd_upvote}
        return self.success(data)
