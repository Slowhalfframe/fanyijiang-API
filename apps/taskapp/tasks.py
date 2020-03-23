from apps.taskapp.celery import app
from django.core.cache import cache

import datetime, time
from apps.questions.models import Answer, Question, QuestionFollow, QAComment

from apps.taskapp.utils import creator_list

from apps.creator.models import CreatorList, SeveralIssues

from apps.articles.models import Article, ArticleComment

from apps.ideas.models import Idea, IdeaComment

from apps.userpage.models import UserProfile

from apps.notifications.models import Notification


# 回答浏览量异步记录
@app.task(name='answers_pv_record')
def answers_pv_record(remote_addr, answer_id):
    today = datetime.date.today()
    today_str = datetime.date.strftime(today, '%Y%m%d')
    redis_key = 'answer_' + str(answer_id) + "_" + today_str
    read_nums = cache.get(redis_key) or 0

    addr_key = remote_addr + '_' + redis_key
    # TODO 是否需要防止同一IP频繁刷新？比如5分钟的刷新次数浏览量只算1次浏览量
    if not cache.get(addr_key):
        # 不存在则说明第一次访问或者已经超过一个小时，PV加1
        cache.set(redis_key, int(read_nums) + 1, 60 * 60 * 24 * 30)  # 设置时常为30天
        # 存入访问时间
        cache.set(addr_key, 1, 60 * 5)  # 设置5分钟过期时间，value不为空即可


# 文章浏览量异步记录
@app.task(name='articles_pv_record')
def articles_pv_record(remote_addr, article_id):
    today = datetime.date.today()
    today_str = datetime.date.strftime(today, '%Y%m%d')
    redis_key = 'article_' + str(article_id) + "_" + today_str
    read_nums = cache.get(redis_key) or 1
    print(read_nums)
    addr_key = remote_addr + '_' + redis_key
    if not cache.get(addr_key):
        # 不存在则说明第一次访问或者已经超过一个小时，PV加1
        cache.set(redis_key, int(read_nums) + 1, 60 * 60 * 24 * 30)  # 设置时常为30天
        # 存入访问时间
        cache.set(addr_key, 1, 60 * 5)


# 想法浏览量异步记录
@app.task(name='thinks_pv_record')
def thinks_pv_record(remote_addr, think_id):
    today = datetime.date.today()
    today_str = datetime.date.strftime(today, '%Y%m%d')
    redis_key = 'think_' + str(think_id) + "_" + today_str
    read_nums = cache.get(redis_key) or 0
    addr_key = remote_addr + '_' + redis_key
    if not cache.get(addr_key):
        # 不存在则说明第一次访问或者已经超过一个小时，PV加1
        cache.set(redis_key, int(read_nums) + 1, 60 * 60 * 24 * 30)
        # 存入访问时间
        cache.set(addr_key, 1, 60 * 5)


# 问题浏览量异步记录
@app.task(name='question_pv_record')
def question_pv_record(remote_addr, think_id):
    today = datetime.date.today()
    today_str = datetime.date.strftime(today, '%Y%m%d')
    redis_key = 'question_' + str(think_id) + "_" + today_str
    read_nums = cache.get(redis_key) or 0
    addr_key = remote_addr + '_' + redis_key
    if not cache.get(addr_key):
        # 不存在则说明第一次访问或者已经超过一个小时，PV加1
        cache.set(redis_key, int(read_nums) + 1, 60 * 60 * 24 * 30)
        # 存入访问时间
        cache.set(addr_key, 1, 60 * 5)


# 将浏览量定时写入数据库
@app.task(name='read_nums_in_database')
def read_nums_in_database():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    yesterday_str = datetime.date.strftime(yesterday, '%Y%m%d')
    # yesterday_str = datetime.datetime.strftime(yesterday, '%Y%m%d')
    print(yesterday_str)
    # 写入回答阅读量
    write_read_in_database('answer', yesterday_str)
    # 写入文章阅读量
    # TODO
    write_read_in_database('article', yesterday_str)
    # 写入想法阅读量
    # TODO
    write_read_in_database('think', yesterday_str)
    # 问题阅读量
    write_read_in_database('question', yesterday_str)


# 定时写入数据库任务
def write_read_in_database(content_type, yesterday_str):
    content_type_dict = {'answer': Answer, 'article': Article, 'think': Idea, 'question': Question}
    which_model = content_type_dict[content_type]
    cache_key_list = cache.keys(content_type + '_*_' + yesterday_str)
    data_list = [{'nums': cache.get(key), 'id': key.replace(content_type + '_', '').replace('_' + yesterday_str, '')}
                 for key in cache_key_list]
    for data in data_list:
        time.sleep(0.01)
        try:
            instance = which_model.objects.get(pk=data['id'])
            answer_nums = instance.read_nums.filter(object_id=instance.id).first()
            raw_nums = answer_nums.nums if answer_nums else 0
            instance.read_nums.update_or_create(object_id=instance.id, defaults={'nums': raw_nums + int(data['nums'])})
        except Exception as e:
            print(e.args)


# 定时生成创作者中心榜单
@app.task(name='write_creator_in_database')
def write_creator_in_database():
    '''每周一统计写入数据库'''
    date = datetime.date.today()
    data = creator_list(date)
    several_issues_instance = SeveralIssues.objects.last()

    several_issues_nums = several_issues_instance.sort + 1 if several_issues_instance else 1
    several, status = SeveralIssues.objects.update_or_create(sort=several_issues_nums, defaults={
        'title': '第{}期榜单'.format(str(several_issues_nums))})
    create_list = list()

    for item in data:
        c = CreatorList(object_id=item['id'], content_type=item['content_type'], score=item['score'],
                        several_issues=several)
        create_list.append(c)
    CreatorList.objects.bulk_create(create_list)


@app.task(name='notification_handler')
def notification_handler(actor_uid, recipient_uid, verb, action_object_id, **kwargs):
    """
    通知处理器
    :param actor_uid:           触发者对象id
    :param recipient_uid:       接受者对象id，可以是一个或者多个接收者
    :param verb:                str 通知类别
    :param action_object:       Instance 动作对象的实例
    :return:                    None
    """
    NOTIFICATION_TYPE = (
        ('LAN', '赞了你的回答'),  # like answer
        ('LAR', '赞了你的文章'),  # like article
        ('LQAC', '赞了你的评论'),  # like comment回答的评论
        ('LAC', '赞了你的评论'),  # like comment文章的评论
        ('LIC', '赞了你的评论'),  # like comment想法的评论
        # ('LQC', '赞了你的评论'),  # like comment问题的评论
        # ('LRC', '赞了你的评论'),  # like comment文章的评论
        # ('LTC', '赞了你的评论'),  # like comment想法的评论
        ('CAN', '评论了你的回答'),  # comment answer
        ('CAR', '评论了你的文章'),  # comment article
        ('CQ', '评论了你的问题'),  # comment question
        ('CI', '评论了你的想法'),  # comment idea
        ('R', '回复了你'),  # reply
        ('A', '回答了你的问题'),  # answer
        ('AF', '回答了你关注的问题'),  # answer
        ('I', '的提问等你来答'),  # invited
        ('O', '关注了你'),  # follow
    )

    if verb == 'I':
        # 传入问题对象
        action_object = Question.objects.get(pk=action_object_id)
        is_object = actor_uid == action_object.user_id
    elif verb == 'A':
        # 传入回答对象
        action_object = Answer.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.question.user_id
    elif verb == 'O':
        # 传入用户对象
        action_object = UserProfile.objects.get(uid=action_object_id)
        is_object = recipient_uid == action_object_id
    elif verb == 'CAN':
        # 传入评论对象, 评论回答
        action_object = QAComment.objects.get(pk=action_object_id)
        obj = action_object.content_object
        is_object = recipient_uid == obj.user_id
    elif verb == 'CQ':
        # 传入评论对象, 评论问题
        action_object = QAComment.objects.get(pk=action_object_id)
        obj = action_object.content_object
        is_object = recipient_uid == obj.user_id
    elif verb == 'CAR':
        # 传入评论对象，评论文章
        action_object = ArticleComment.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.article.user_id

    elif verb == 'CI':
        action_object = IdeaComment.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.think.user_id

    elif verb == 'AF':
        is_object = False
        action_object = Answer.objects.get(pk=action_object_id)
        if QuestionFollow.objects.filter(user_id=recipient_uid, question=action_object.question).exists():
            is_object = True

    elif verb == 'LAN':
        # 赞了你的回答
        action_object = Answer.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.user_id

    elif verb == 'LAR':
        # 赞了你的文章
        action_object = Article.objects.get(pk=action_object_id, is_deleted=False)
        is_object = recipient_uid == action_object.user_id

    elif verb == 'LQAC':
        # 赞了你的问题或回答的评论
        action_object = QAComment.objects.get(pk=action_object_id)
        obj = action_object.content_object
        is_object = recipient_uid == obj.user_id

    elif verb == 'LAC':
        # 赞了你的文章的评论
        action_object = ArticleComment.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.user_id

    elif verb == 'LIC':
        action_object = IdeaComment.objects.get(pk=action_object_id)
        is_object = recipient_uid == action_object.user_id

    else:
        is_object = recipient_uid == action_object_id

    is_actor = actor_uid != recipient_uid

    if is_actor and is_object:
        # 只通知接收者，即recipient == 动作对象的作者
        # 记录通知内容
        actor = UserProfile.objects.get(uid=actor_uid)
        recipient = UserProfile.objects.get(uid=recipient_uid)
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )
