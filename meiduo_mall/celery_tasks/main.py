import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")
#创建celery实例
app = Celery('celery_tasks')

#配置中间人的信息
app.config_from_object('celery_tasks.config')


#加载生产者的信息
app.autodiscover_tasks(['celery_tasks.sms'])








