# apps/core/tasks.py
from celery import shared_task
from core.services.task_runner import run_search_task as sync_task
from core.models import SearchTask


@shared_task
def run_search_task(task_id):
    task = SearchTask.objects.get(id=task_id)
    return sync_task(task)
