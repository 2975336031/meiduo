# 此文件中编写celery客户端代码
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 1. 创建celery客户端对象
celery_app = Celery('meiduo')

# 2. 加载celery配置信息(仓库/消息队列是谁?在哪里?)
celery_app.config_from_object('celery_tasks.config')

# 3. celery可以生产什么任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
