from kombu import Queue, Exchange

BROKER_URL = 'redis://127.0.0.1:6379/15'
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'  # 定时任务
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/15'
CELERY_ACCEPT_CONTENT = ['application/json', 'msgpack']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERYD_CONCURRENCY = 4  # worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
CELERYD_MAX_TASKS_PER_CHILD = 150  # 每个worker执行了多少任务就会死掉，默认是无限的


# 创建Queue的实例时
CELERY_QUEUES = (
    Queue('answers_pv_queue', Exchange("answers_pv_queue"), routing_key='answer_router'),
    Queue('articles_pv_queue', Exchange("articles_pv_queue"),routing_key='article_router'),
    Queue('thinks_pv_queue', Exchange("thinks_pv_queue"),routing_key='think_router'),
    Queue('write_in_db', Exchange("write_in_db"),routing_key='in_db_router'),
    Queue('write_creator_list_db', Exchange("write_creator_list_db"),routing_key='creator_list'),
)
#
CELERY_ROUTES = {
    'answers_pv_record': {
        'queue': 'answers_pv_queue',
        'routing_key': 'answer_router',
    },
    'articles_pv_record': {
        'queue': 'articles_pv_queue',
        'routing_key': 'article_router',
    },
    'thinks_pv_record': {
        'queue': 'thinks_pv_queue',
        'routing_key': 'think_router',
    },
    'read_nums_in_database': {
        'queue': 'write_in_db',
        'routing_key': 'in_db_router',
    },
    'write_creator_in_database': {
        'queue': 'write_creator_list_db',
        'routing_key': 'creator_list',
    },

}
from datetime import timedelta
from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'read_nums_in_database': {
        # task就是需要执行计划任务的函数
         'task': 'read_nums_in_database',
         # 配置计划任务的执行时间，每天1点执行任务
         'schedule': crontab(hour=1, minute=0),
         # 传入给计划任务函数的参数
         'args': ()
    },

    'write_creator_in_database': {
        # task就是需要执行计划任务的函数
        'task': 'write_creator_in_database',
        # 配置计划任务的执行时间，没周一6点更新
        'schedule': crontab(day_of_week=1, hour=6, minute=0),
        # 传入给计划任务函数的参数
        'args': ()
    },
}