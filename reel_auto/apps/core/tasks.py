from celery import shared_task
from core.models import SearchTask
from core.services.task_runner import run_task_logic


@shared_task
def run_search_task_async(task_id):
    task = SearchTask.objects.get(id=task_id)
    return run_task_logic(task)
