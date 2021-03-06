import os
from celery import Celery, platforms

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base_setting'

app = Celery("celery_tasks")
app.config_from_object('apps.taskapp.conf')

app.autodiscover_tasks(["apps.taskapp"])

platforms.C_FORCE_ROOT=True