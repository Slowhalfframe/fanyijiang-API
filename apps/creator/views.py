import datetime, random

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.core.cache import cache

from apps.utils.api import CustomAPIView

from apps.questions.models import Answer, Question, QuestionFollow, QuestionInvite

from apps.userpage.models import UserProfile

from apps.creator.models import ReadNums, CreatorList, SeveralIssues

from apps.articles.models import Article

from apps.labels.models import LabelFollow

from apps.ideas.models import Idea


# 基础统计
class BaseStatistics(object):
    def __init__(self, user, which_model):
        self.user = user
        self.which_model = which_model

    def get_queryset(self):
        queryset = self.which_model.objects.filter(user_id=self.user.uid)
        return queryset

    def get_instance(self, instance_id):
        instance = self.which_model.objects.get(pk=instance_id)
        return instance


# 阅读量统计
class ReadNumsClass(BaseStatistics):

    def __init__(self, user, which_model):
        super(ReadNumsClass, self).__init__(user=user, which_model=which_model)

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        try:
            read_nums = instance.read_nums.get(object_id=id).nums
        except Exception as e:
            print(e.args)
            read_nums = 0
        return read_nums

    def get_instance_date_nums(self, id, date, cache_key=None):
        nums = cache.get(cache_key + '_' + str(id) + '_' + date) or 0
        return nums

    def get_queryset_date_num(self, date, cache_key=None):
        yesterday_nums_list = [cache.get(cache_key + '_' + str(instance.id) + '_' + date) or 0 for
                               instance in self.get_queryset()]
        nums = sum(yesterday_nums_list) or 0
        return nums

    def get_queryset_total_num(self):
        instance_id_list = [instance.id for instance in self.get_queryset()]
        content_type = ContentType.objects.get(app_label=self.which_model._meta.app_label,
                                               model=self.which_model._meta.model_name)
        read_instance = ReadNums.objects.filter(object_id__in=instance_id_list,
                                                content_type=content_type).aggregate(nums=Sum('nums'))
        total_nums = read_instance['nums'] or 0
        return total_nums


# 回答阅读量统计
class AnswerReadNums(ReadNumsClass):

    def __init__(self, user, which_model=Answer):
        super(AnswerReadNums, self).__init__(user=user, which_model=which_model)

    def get_queryset_date_num(self, date, cache_key='answer'):
        return super(AnswerReadNums, self).get_queryset_date_num(date, cache_key=cache_key)

    def get_instance_date_nums(self, id, date, cache_key='answer'):
        return super(AnswerReadNums, self).get_instance_date_nums(id=id, date=date, cache_key=cache_key)

    def get_instance_total_nums(self, id):
        return super(AnswerReadNums, self).get_instance_total_nums(id=id)


# 文章阅读量统计
class ArticleReadNums(ReadNumsClass):

    def __init__(self, user, which_model=Article):
        super(ArticleReadNums, self).__init__(user=user, which_model=which_model)

    def get_queryset_date_num(self, date, cache_key='article'):
        return super(ArticleReadNums, self).get_queryset_date_num(date, cache_key=cache_key)

    def get_instance_date_nums(self, id, date, cache_key='article'):
        return super(ArticleReadNums, self).get_instance_date_nums(id=id, date=date)

    def get_instance_total_nums(self, id):
        return super(ArticleReadNums, self).get_instance_total_nums(id=id)


# 想法阅读量统计
class ThinkReadNums(ReadNumsClass):
    def __init__(self, user, which_model=Idea):
        super(ThinkReadNums, self).__init__(user=user, which_model=which_model)

    def get_queryset_date_num(self, date, cache_key='think'):
        return super(ThinkReadNums, self).get_queryset_date_num(date, cache_key=cache_key)

    def get_instance_date_nums(self, id, date, cache_key='think'):
        return super(ThinkReadNums, self).get_instance_date_nums(id=id, date=date)

    def get_instance_total_nums(self, id):
        return super(ThinkReadNums, self).get_instance_total_nums(id=id)


# 回答评论统计
class AnswerCommentStatistics(BaseStatistics):
    '''回答评论统计'''

    def __init__(self, user, which_model=Answer):
        super(AnswerCommentStatistics, self).__init__(user=user, which_model=which_model)

    def get_total_comment_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.comment.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_total_comments(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.comment.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for query in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.comment.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.comment.all().count()
        return nums


# 回答收藏统计
class AnswerCollectStatistics(BaseStatistics):
    '''回答收藏统计'''

    def __init__(self, user, which_model=Answer):
        super(AnswerCollectStatistics, self).__init__(user=user, which_model=which_model)

    def get_total_collect_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.collect.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_collect_nums(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.collect.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for query in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_collect_date_nums(self, id, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        instance = self.get_instance(id)
        end_date = begin_date + datetime.timedelta(days=1)
        nums_list = instance.collect.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        nums = sum(nums_list) or 0
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.collect.all().count()
        return nums


class AnswerVoteStatistics(BaseStatistics):
    '''回答赞同统计'''

    def __init__(self, user, which_model=Answer):
        super(AnswerVoteStatistics, self).__init__(user, which_model)

    def get_total_upvote_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.vote.filter(value=True).count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_upvote_nums(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.vote.filter(value=True, create_at__gte=begin_date, create_at__lte=end_date).count() for query
                     in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_upvote_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.vote.filter(value=True, create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.vote.filter(value=True).count()
        return nums


# 文章评论收统计
class ArticleCommentStatistics(BaseStatistics):
    '''文章评论统计'''

    def __init__(self, user, which_model=Article):
        super(ArticleCommentStatistics, self).__init__(user=user, which_model=which_model)

    def get_total_comment_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.articlecomment_set.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_total_comments(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.articlecomment_set.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for
                     query in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.articlecomment_set.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.articlecomment_set.all().count()
        return nums


# 文章收藏统计
class ArticleCollectStatistics(BaseStatistics):
    '''文章收藏统计'''

    def __init__(self, user, which_model=Article):
        super(ArticleCollectStatistics, self).__init__(user=user, which_model=which_model)

    def get_total_collect_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.mark.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_collect_nums(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.mark.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for query in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.mark.all().count()
        return nums

    def get_instance_collect_date_nums(self, id, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        instance = self.get_instance(id)
        end_date = begin_date + datetime.timedelta(days=1)
        nums_list = instance.mark.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        nums = sum(nums_list) or 0
        return nums


class ArticleVoteStatistics(BaseStatistics):
    '''文章赞同统计'''

    def __init__(self, user, which_model=Article):
        super(ArticleVoteStatistics, self).__init__(user, which_model)

    def get_total_upvote_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.vote.filter(value=True).count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_upvote_nums(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.vote.filter(value=True, create_at__gte=begin_date, create_at__lte=end_date).count() for query
                     in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_upvote_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.vote.filter(value=True, create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_upvote_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.vote.all().count()
        return nums


# 文章评论收统计
class ThinkCommentStatistics(BaseStatistics):
    '''想法评论统计'''

    def __init__(self, user, which_model=Idea):
        super(ThinkCommentStatistics, self).__init__(user=user, which_model=which_model)

    def get_total_comment_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.ideacomment_set.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_total_comments(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.ideacomment_set.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for
                     query in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.ideacomment_set.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.ideacomment_set.all().count()
        return nums


class ThinkVoteStatistics(BaseStatistics):
    '''想法赞同统计'''

    def __init__(self, user, which_model=Idea):
        super(ThinkVoteStatistics, self).__init__(user, which_model)

    def get_total_upvote_nums(self):
        queryset = self.get_queryset()
        nums_list = [query.agree.all().count() for query in queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_date_upvote_nums(self, date):
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        queryset = self.get_queryset()
        nums_list = [query.agree.filter(create_at__gte=begin_date, create_at__lte=end_date).count() for query
                     in
                     queryset]
        nums = sum(nums_list) or 0
        return nums

    def get_instance_upvote_date_nums(self, id, date):
        instance = self.get_instance(id)
        begin_date = datetime.datetime.strptime(date, '%Y%m%d')
        end_date = begin_date + datetime.timedelta(days=1)
        nums = instance.agree.filter(create_at__gte=begin_date, create_at__lte=end_date).count()
        return nums

    def get_instance_upvote_total_nums(self, id):
        instance = self.get_instance(id)
        nums = instance.agree.all().count()
        return nums


# 问题推荐
class RecommendQuestion(object):
    '''
    大致实现思路:
        首先获取用户关注的标签,获取标签下所有用户未回答的问题
        如果获取的问题数量不够显示,则从所有未回答的问题内随机添加,直到数量达标
    '''

    def __init__(self, user, offset, limit):
        self.user = user
        self.offset = int(offset)
        self.limit = int(limit)

    def get_user_followed_labels(self):
        '''获取用户关注的所有话题'''
        labels = LabelFollow.objects.filter(user_id=self.user.uid)
        return labels

    def get_label_question(self, label):
        '''获取用户关注的话题下所有未回答过的问题'''
        questions = label.label.question_set.exclude(answer__user_id=self.user.uid)[
                    self.offset:self.offset + self.limit]
        question_list = [question for question in questions]
        return question_list

    def get_all_question(self):
        '''获取所有问题中，用户未回答过的问题'''
        questions = Question.objects.exclude(answer__user_id=self.user.uid).order_by('-create_at')[
                    self.offset:self.offset + self.limit]
        question_list = [question for question in questions]
        return question_list

    def get_random_any_question(self, question_list, limit):
        '''随机多个'''
        re_questions = random.sample(question_list, limit) if len(question_list) >= limit else question_list
        return re_questions

    def get_random_one_question(self, question_list):
        '''随机获取1个'''
        re_question = random.choice(question_list) if len(question_list) >= 1 else question_list
        return re_question

    def get_finally_question(self, ):
        '''获取推荐问题列表'''
        labels = self.get_user_followed_labels()
        questions = list()
        if len(labels):
            for label in labels:
                label_question = self.get_label_question(label)
                # 判断是否有问题存在，不存在则从所有问题内添加
                if len(label_question): questions.extend(label_question)

        q = self.get_all_question()

        # print(self.limit)
        # print(len(questions))
        # 若question不足limit的数量,依次从全部问题内添加
        while len(questions) < self.limit:
            if not len(q):
                break
            random_q = self.get_random_one_question(q)
            if random_q not in questions:
                questions.append(random_q)
            q.remove(random_q)
        return questions

    def get_json_data(self, data_list):
        data_l = list()
        for question in data_list:
            data = {}
            data['id'] = question.id
            data['title'] = question.title
            data['content'] = question.content
            data['follow_count'] = QuestionFollow.objects.filter(question=question).count()
            data['answer_count'] = question.answer_set.all().count()
            data_l.append(data)
        return data_l

    def get_re_json_data(self):
        '''获取推荐问题'''
        finally_list = self.get_finally_question()
        data = self.get_json_data(finally_list)
        return data

    def get_new_question(self):
        '''获取最新问题'''
        finally_list = self.get_all_question()
        data = self.get_json_data(finally_list)
        return data


# 最近创作数据
class RecentCreateContent(object):
    def __init__(self, user):
        self.user = user

    def recent_answer(self):
        answers = Answer.objects.filter(user_id=self.user.uid).order_by('-create_at')[:3]
        answer_data = []
        for answer in answers:
            data = dict()
            data['id'] = answer.id
            data['display_title'] = answer.question.title
            data['display_content'] = answer.content
            data['type'] = 'answer'
            data['create_at'] = answer.create_at
            read_nums = answer.read_nums.filter(object_id=answer.id).first()
            data['read_nums'] = read_nums.nums if read_nums else 0
            # 获取阅读量
            data['comment_count'] = answer.comment.filter(object_id=answer.id).count()
            # 赞同量
            data['upvote_count'] = answer.vote.filter(object_id=answer.id, value=True).count()
            # 收藏量
            data['collect_count'] = answer.collect.filter(object_id=answer.id).count()
            answer_data.append(data)
        return answer_data

    def recent_article(self):
<<<<<<< Updated upstream
        articles = Article.objects.filter(user_id=self.user.uid, is_deleted=False).order_by('create_at')[:3]
=======
        articles = Article.objects.filter(user_id=self.user.uid, status='published', is_deleted=False).order_by('create_at')[:3]
>>>>>>> Stashed changes
        article_data = []
        for article in articles:
            data = dict()
            data['id'] = article.id
            data['display_title'] = article.title
            data['display_content'] = article.content
            data['type'] = 'article'
            data['create_at'] = article.create_at
            read_nums = article.read_nums.filter(object_id=article.id).first()
            data['read_nums'] = read_nums.nums if read_nums else 0
            data['comment_count'] = article.articlecomment_set.all().count()
            data['upvote_count'] = article.vote.filter(object_id=article.id, value=True).count()
            data['collect_count'] = article.mark.filter(object_id=article.id).count()
            article_data.append(data)
        return article_data

    def recent_thinks(self):
        thinks = Idea.objects.filter(user_id=self.user.uid).order_by('create_at')[:3]
        thinks_data = []
        for think in thinks:
            data = dict()
            data['id'] = think.id
            data['display_title'] = ''
            data['display_content'] = think.content
            data['type'] = 'think'
            data['create_at'] = think.create_at
            read_nums = think.read_nums.filter(object_id=think.id).first()
            data['read_nums'] = read_nums.nums if read_nums else 0
            data['comment_count'] = think.ideacomment_set.all().count()
            data['upvote_count'] = think.agree.filter(object_id=think.id).count()
            data['collect_count'] = 0
            thinks_data.append(data)
        return thinks_data

    def get_recent_data(self):
        recent_list = self.recent_answer() + self.recent_article() + self.recent_thinks()
        recent_data = sorted(recent_list, key=lambda x: x['create_at'], reverse=True)[:3]
        return recent_data


# 总阅读量统计
class TotalNums(object):
    def __init__(self, user):
        self.user = user

    def get_total_nums(self):
        answer = AnswerReadNums(self.user).get_queryset_total_num() or 0
        article = ArticleReadNums(self.user).get_queryset_total_num() or 0
        think = ThinkReadNums(self.user).get_queryset_total_num() or 0
        return answer + article + think

    def get_date_total_nums(self, date):
        answer = AnswerReadNums(self.user).get_queryset_date_num(date) or 0
        article = ArticleReadNums(self.user).get_queryset_date_num(date) or 0
        think = ThinkReadNums(self.user).get_queryset_date_num(date) or 0
        return answer + article + think

    def get_total_vote(self):
        '''所有赞同的数量'''
        answer = AnswerVoteStatistics(self.user).get_total_upvote_nums() or 0
        article = AnswerVoteStatistics(self.user).get_total_upvote_nums() or 0
        think = AnswerVoteStatistics(self.user).get_total_upvote_nums() or 0
        return answer + article + think

    def get_date_total_votes(self, date):
        '''某一个日期赞同的总数'''
        answer = AnswerVoteStatistics(self.user).get_date_upvote_nums(date) or 0
        article = AnswerVoteStatistics(self.user).get_date_upvote_nums(date) or 0
        think = AnswerVoteStatistics(self.user).get_date_upvote_nums(date) or 0
        return answer + article + think


from apps.utils.decorators import validate_identity


class CreatorHomeAPIView(CustomAPIView):
    '''创作者中心主页视图，包含阅读量，赞同数，关注者等问题推荐'''

    @validate_identity
    def get(self, request):
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        # 阅读量
        total_instance = TotalNums(user)
        total_read_nums = total_instance.get_total_nums()

        # 昨日总阅读量
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_str = datetime.date.strftime(yesterday, '%Y%m%d')
        total_ysd_read_nums = total_instance.get_date_total_nums(yesterday_str)
        # 关注量

        # 粉丝总数
        fans = UserProfile.objects.filter(as_fans__idol__uid=uid)
        # 昨日新增粉丝数
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        ysd_fans = UserProfile.objects.filter(as_fans__idol__uid=uid, as_fans__create_time__gte=yesterday,
                                              as_fans__create_time__lte=today)

        # TODO 赞同总数
        total_upvote = total_instance.get_total_vote()
        ysd_upvote = total_instance.get_date_total_votes(yesterday_str)

        # 近日创作数据
        # 从文章和回答中各取三个对象，比较时间，取最近的三个
        recent_instance = RecentCreateContent(user)
        recent_data = recent_instance.get_recent_data()

        data = {
            'creator_data': {
                'read_nums': {'total_read_nums': total_read_nums, 'total_ysd_read_nums': total_ysd_read_nums},
                'fans': {'total_fans': fans.count(), 'ysd_add_fans': ysd_fans.count()},
                'upvotes': {'total_upvote': total_upvote, 'ysd_upvote': ysd_upvote}},
            'recent_data': recent_data,
        }
        return self.success(data)


class CreatorDataDetailAPIView(CustomAPIView):
    '''创作者中心内容分析页面顶部内容视图'''

    @validate_identity
    def get(self, request):
        # uid = request.GET.get('uid')
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        include = request.GET.get('include')

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = datetime.date.strftime(yesterday, '%Y%m%d')
        if not include:
            return self.error('缺少include', 400)
        create_data = {}
        if include == 'answer':
            instance = AnswerReadNums(user=user)
            create_data = {
                'total_count': instance.get_queryset().count(),
                'read_nums': instance.get_queryset_total_num(),
                'upvote_nums': AnswerVoteStatistics(user).get_total_upvote_nums(),
                'ysd_read_nums': instance.get_queryset_date_num(yesterday_str),
                'ysd_upvote_nums': AnswerVoteStatistics(user).get_date_upvote_nums(yesterday_str)
            }

        if include == 'article':
            instance = ArticleReadNums(user=user)
            create_data = {
                'total_count': instance.get_queryset().count(),
                'read_nums': instance.get_queryset_total_num(),
                'upvote_nums': ArticleVoteStatistics(user).get_total_upvote_nums(),
                'ysd_read_nums': instance.get_queryset_date_num(yesterday_str),
                'ysd_upvote_nums': ArticleVoteStatistics(user).get_date_upvote_nums(yesterday_str)
            }

        if include == 'think':
            instance = ThinkReadNums(user=user)
            create_data = {
                'total_count': instance.get_queryset().count(),
                # 'read_nums': instance.get_queryset_total_num(),
                'upvote_nums': ThinkVoteStatistics(user).get_total_upvote_nums(),  # TODO
                'ysd_read_nums': instance.get_queryset_date_num(yesterday_str),
                'ysd_upvote_nums': ThinkVoteStatistics(user).get_date_upvote_nums(yesterday_str),  # TODO
                'comment_count': sum([query.ideacomment_set.all().count() for query in instance.get_queryset()]),
                'ysd_comment_count': sum(
                    [query.ideacomment_set.filter(create_at__gte=yesterday, create_at__lte=today).count() for query in
                     instance.get_queryset()])
            }
        return self.success(create_data)


class StatisticsDateAPIView(CustomAPIView):
    '''创作者中心内容分析页面详细分析视图'''

    @validate_identity
    def get(self, request):
        # uid = request.GET.get('uid')
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        data_type = request.GET.get('data_type')

        begin_date = request.GET.get('begin_date')
        end_date = request.GET.get('end_date')
        if begin_date and end_date:
            begin_da = datetime.datetime.strptime(begin_date, '%Y%m%d')
            end_da = datetime.datetime.strptime(end_date, '%Y%m%d')
        else:
            end_da = datetime.date.today()
            begin_da = end_da - datetime.timedelta(days=7)

        if not data_type:
            return self.error('请选择数据类型', 404)

        data_list = []
        while begin_da < end_da:
            data = {}
            statistics_date = datetime.date.strftime(begin_da, '%Y%m%d')
            data['statistics_date'] = statistics_date
            if data_type == 'article':
                data['read_nums'] = ArticleReadNums(user).get_queryset_date_num(statistics_date)
                data['comment_nums'] = ArticleCommentStatistics(user).get_date_total_comments(statistics_date)
                data['upvote_nums'] = ArticleVoteStatistics(user).get_date_upvote_nums(statistics_date)
                data['collect_nums'] = ArticleCollectStatistics(user).get_date_collect_nums(statistics_date)

            if data_type == 'answer':
                data['read_nums'] = AnswerReadNums(user).get_queryset_date_num(statistics_date)
                data['comment_nums'] = AnswerCommentStatistics(user).get_date_total_comments(statistics_date)
                data['upvote_nums'] = AnswerVoteStatistics(user).get_date_upvote_nums(statistics_date)
                data['collect_nums'] = AnswerCollectStatistics(user).get_date_collect_nums(statistics_date)

            if data_type == 'think':
                data['read_nums'] = ThinkReadNums(user).get_queryset_date_num(statistics_date)
                data['comment_nums'] = ThinkCommentStatistics(user).get_date_total_comments(statistics_date)
                data['upvote_nums'] = ThinkVoteStatistics(user).get_date_upvote_nums(statistics_date)

            begin_da += datetime.timedelta(days=1)
            data_list.append(data)
        return self.success(data_list)


class SingleDataStatisticsAPIView(CustomAPIView):
    '''内容分析页面单篇内容分析'''

    @validate_identity
    def get(self, request):
        # uid = request.GET.get('uid')
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        data_type = request.GET.get('data_type')
        begin_date = request.GET.get('begin_date')
        end_date = request.GET.get('end_date')

        if begin_date and end_date:
            begin_da = datetime.datetime.strptime(begin_date, '%Y%m%d')
            end_da = datetime.datetime.strptime(end_date, '%Y%m%d')
        else:
            end_da = datetime.date.today()
            begin_da = end_da - datetime.timedelta(days=7)
        data_list = list()
        if data_type == 'answer':
            answers = Answer.objects.filter(create_at__gte=begin_da, create_at__lte=end_da, user_id=uid)
            for answer in answers:
                data = dict()
                data['id'] = answer.id
                data['q_id'] = answer.question.id
                data['title'] = answer.content[:8] + '...' if len(answer.content) > 8 else answer.content
                data['create_at'] = answer.create_at
                data['read_nums'] = AnswerReadNums(user).get_instance_total_nums(answer.id)
                data['comment_nums'] = AnswerCommentStatistics(user).get_instance_total_nums(answer.id)
                data['upvote_nums'] = AnswerVoteStatistics(user).get_instance_total_nums(answer.id)
                data['collect_nums'] = AnswerCollectStatistics(user).get_instance_total_nums(answer.id)
                data_list.append(data)

        if data_type == 'article':
<<<<<<< Updated upstream
            articles = Article.objects.filter(create_at__gte=begin_da, create_at__lte=end_da, user_id=uid,
                                              is_deleted=False)
=======
            articles = Article.objects.filter(create_at__gte=begin_da, create_at__lte=end_da, user_id=uid, status='published', is_deleted=False)
>>>>>>> Stashed changes
            for article in articles:
                data = dict()
                data['id'] = article.id
                data['title'] = article.title[:8] + '...' if len(article.title) > 8 else article.title
                data['create_at'] = article.create_at
                data['read_nums'] = ArticleReadNums(user).get_instance_total_nums(article.id)
                data['comment_nums'] = ArticleCommentStatistics(user).get_instance_total_nums(article.id)
                data['upvote_nums'] = ArticleVoteStatistics(user).get_instance_upvote_total_nums(article.id)
                data['collect_nums'] = ArticleCollectStatistics(user).get_instance_total_nums(article.id)
                data_list.append(data)
        if data_type == 'think':
            thinks = Idea.objects.filter(create_at__gte=begin_da, create_at__lte=end_da, user_id=uid)
            for think in thinks:
                data = dict()
                data['id'] = think.id
                data['title'] = think.content[:8] + '...' if len(think.content) > 8 else think.content
                data['create_at'] = think.create_at
                data['read_nums'] = ThinkReadNums(user).get_instance_total_nums(think.id)
                data['comment_nums'] = ThinkCommentStatistics(user).get_instance_total_nums(think.id)
                data['upvote_nums'] = ArticleVoteStatistics(user).get_instance_upvote_total_nums(think.id)
                data_list.append(data)
        return self.success(data_list)


class RecommendQuestionAPIVIew(CustomAPIView):
    '''问题推荐视图'''

    @validate_identity
    def get(self, request):
        # uid = request.GET.get('uid')
        uid = request._request.uid
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 20)
        question_type = request.GET.get('question_type', 'recommend')
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)

        recommend = RecommendQuestion(user, offset=offset, limit=limit)
        data = []
        if question_type == 'recommend':
            # 为你推荐
            data = recommend.get_re_json_data()

        if question_type == 'new':
            # 最新问题
            data = recommend.get_new_question()

        if question_type == 'invited':
            # 邀请你回答
            invited = QuestionInvite.objects.filter(invited=uid, status=0)
            question_list = [i.question for i in invited]

            data = recommend.get_json_data(question_list)

        return self.success(data)


class CreatorListAPIView(CustomAPIView):
    def get(self, request):
        '''查看所有榜单'''
        params_query = request.query_params.dict()
        if params_query.get('several_id'):
            s = SeveralIssues.objects.filter(pk=params_query.get('several_id')).first()
            if not s:
                return self.error('error', 400)
            contents = s.creator_list.all()
            creator_list = list()
            for content in contents:
                data = {}
                data['id'] = content.object_id
                content_type = content.content_type
                if content_type == 'answer':
                    answer = Answer.objects.get(pk=data['id'])
                    data['title'] = answer.question.title
                    user = UserProfile.objects.get(uid=answer.user_id)
                    user_data = {'avatar': user.avatar, 'nickname': user.nickname}
                    data['author_data'] = user_data
                    data['score'] = content.score

                if content_type == 'article':
                    article = Article.objects.get(pk=data['id'], is_deleted=False)
                    data['title'] = article.title
                    user = UserProfile.objects.get(uid=article.user_id)
                    user_data = {'avatar': user.avatar, 'nickname': user.nickname}
                    data['author_data'] = user_data
                    data['score'] = content.score
                data['content_type'] = content_type
                creator_list.append(data)
            return self.success(creator_list)

        else:
            several = SeveralIssues.objects.all().order_by('-create_at')
            data = [{'title': s.title, 'image': s.image, 'id': s.id} for s in several]
            return self.success(data)
