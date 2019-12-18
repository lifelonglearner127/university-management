import os
from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'config.settings.local'
)

app = Celery('school')

app.config_from_object('config.celeryconfig', namespace='CELERY')

app.autodiscover_tasks()
