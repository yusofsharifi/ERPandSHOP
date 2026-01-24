from celery import Celery
import os

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)

celery_app = Celery('backend', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.conf.task_routes = {'app.tasks.treasury_tasks.*': {'queue': 'treasury'}}

# autodiscover tasks module
celery_app.autodiscover_tasks(['app.tasks'])
