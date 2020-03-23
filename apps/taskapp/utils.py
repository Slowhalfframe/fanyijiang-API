import datetime

from apps.questions.models import Question, Answer

from apps.articles.models import Article

from apps.userpage.models import UserProfile


def creator_list(date):
    '''统计一周内创作数据的致知数
    # 致知指数 = 60*[30*内容评级+15*阅读赞同比]+40*[30*赞同+15*分享+10*收藏+5*评论-10*举报-30*反对]
    致知指数 = 60*[15*阅读赞同比]+40*[30*赞同+10*收藏+5*评论-30*反对]
    每周一上午6点统计上周创作数据榜, 每个榜单为10个内容
    '''
    # 1. 先统计回答内容
    begin_date = date - datetime.timedelta(days=8)
    end_date = date - datetime.timedelta(days=1)
    # 获取上周创作的回答内容
    answers = Answer.objects.filter(create_at__gte=begin_date, create_at__lte=end_date)
    articles = Article.objects.filter(create_at__gte=begin_date, create_at__lte=end_date, status='published', is_deleted=False)
    answer_data = [
        {'content_type': 'answer', 'id': answer.id, 'title': answer.question.title, 'score': get_answer_score(answer),
         } for answer in answers]
    article_data = [
        {'content_type': 'article', 'id': article.id, 'title': article.title, 'score': get_article_score(article),
         } for article in articles]

    all_data = answer_data + article_data

    data = sorted(all_data, key=lambda x: x['score'], reverse=True)[:10]
    return data


def get_answer_score(answer):
    # 获取一周的阅读量, 因为统计的是从回答从创建到昨日的阅读量, 所以可以直接从数据库读即可
    read_nums = answer.read_nums.get(object_id=answer.id).nums or 0
    up_votes = answer.vote.filter(object_id=answer.id, value=True).count() or 1
    down_votes = answer.vote.filter(object_id=answer.id, value=False).count()
    comments = answer.comment.all().count()
    collects = answer.collect.all().count()

    score = 60 * (15 * (read_nums / up_votes)) + 40 * (5 * comments + 30 * up_votes + 10 * collects - 30 * down_votes)
    return score


def get_article_score(article):
    read = article.read_nums.filter(object_id=article.id).first()
    read_nums = read.nums if read else 0
    up_votes = article.vote.filter(object_id=article.id, value=True).count() or 1
    down_votes = article.vote.filter(object_id=article.id, value=False).count()
    comments = article.articlecomment_set.all().count()
    collects = article.mark.all().count()
    score = 60 * (15 * (read_nums / up_votes)) + 40 * (5 * comments + 30 * up_votes + 10 * collects - 30 * down_votes)
    return score
