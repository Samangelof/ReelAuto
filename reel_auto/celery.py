# reel_auto/celery.py
import os
import sys

import django
from celery import Celery


sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")


# django.setup()

app = Celery("reel_auto")
app.config_from_object("django.conf:settings", namespace="CELERY")

print("Using broker:", app.conf.broker_url)

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')