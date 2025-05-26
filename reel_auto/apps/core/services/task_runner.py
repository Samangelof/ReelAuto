# core/services/task_runner.py
import logging
from core.services.hikerapi_client import HikerAPIClient
from core.services.hiker_reels_processor import HikerReelsProcessor
from decouple import config

logger = logging.getLogger(__name__)


def _extract_first_hashtag(keywords: str) -> str:
    if not keywords:
        return None
    for word in keywords.split():
        word = word.strip().strip(',')  # убрать пробелы и запятые
        if word.startswith('#'):
            return word[1:]
    return None



def run_task_logic(task):
    from core.models import SearchResult
    from io import StringIO
    from django.core.files.base import ContentFile
    import csv

    api = HikerAPIClient(config("HIKER_API_KEY"))
    processor = HikerReelsProcessor(api)

    hashtag = _extract_first_hashtag(task.keywords)
    if not hashtag:
        raise ValueError("Не указан хэштег для задачи поиска")
    
    logger.warning(f"[TASK #{task.id}] 🚨 Запрос к HikerAPI будет тарифицирован (~$0.02). " 
               f"Хэштег: #{hashtag} | лимит: {task.limit} | фильтры: views>={task.views_from or 0}, "
               f"likes>={task.likes_from or 0}, comments>={task.comments_from or 0}")


    try:
        reels = processor.fetch_and_filter(
            hashtag=hashtag,
            min_views=task.views_from or 0,
            min_likes=task.likes_from or 0,
            min_comments=task.comments_from or 0,
            date_from=task.date_from,
            date_to=task.date_to,
            limit=task.limit
        )
    except Exception as e:
        logger.exception(f"[TASK #{task.id}] Ошибка при выполнении задачи: {e}")
        task.status = 'error'
        task.save()
        return 0

    for reel in reels:
        SearchResult.objects.create(task=task, **reel)

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Ссылка", "Автор", "Дата", "Описание", "Хэштеги", "Просмотры", "Лайки", "Комментарии", "Звук"])
    for reel in reels:
        writer.writerow([
            reel["video_url"],
            reel["author_username"],
            reel["published_at"],
            reel["description"],
            reel["hashtags"],
            reel["views"],
            reel["likes"],
            reel["comments"],
            reel["sound_url"]
        ])

    filename = f"reels_task_{task.id}.csv"
    task.csv_file.save(filename, ContentFile(csv_buffer.getvalue().encode()), save=True)

    task.status = 'done'
    task.save()

    logger.info(f"[TASK #{task.id}] Завершено. Сохранено {len(reels)} рилсов.")
    return len(reels)