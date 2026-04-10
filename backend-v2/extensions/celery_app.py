"""
Celery配置
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')

app = Celery('lims')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
