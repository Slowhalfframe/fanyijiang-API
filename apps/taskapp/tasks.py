from apps.taskapp.celery import app
from django.core.cache import cache

import datetime, time
from apps.questions.models import Answer

from apps.taskapp.utils import creator_list

from apps.creator.models import CreatorList, SeveralIssues

from apps.articles.models import Article

from apps.ideas.models import Idea


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


@app.task(name='read_nums_in_database')
def read_nums_in_database():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    yesterday_str = datetime.date.strftime(yesterday, '%Y%m%d')
    # yesterday_str = datetime.datetime.strftime(today, '%Y%m%d')
    print(yesterday_str)
    # 写入回答阅读量
    write_read_in_database('answer', yesterday_str)
    # 写入文章阅读量
    # TODO
    write_read_in_database('article', yesterday_str)
    # 写入想法阅读量
    # TODO
    write_read_in_database('think', yesterday_str)


# 定时写入数据库任务
def write_read_in_database(content_type, yesterday_str):
    content_type_dict = {'answer': Answer, 'article': Article, 'think': Idea}
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
