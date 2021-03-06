from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labonclick.settings')
BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')
app = Celery('labonclick')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# uncoment for docker
app.conf.broker_url = 'redis://redis:6379'

# comment for docker
#app.conf.broker_url = 'redis://127.0.0.1:6379'

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

