import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')

celery = Celery('storefront')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()

# celery -A storefront worker --loglevel=INFO  -P threads
# celery -A storefront beat
# celery -A storefront flower