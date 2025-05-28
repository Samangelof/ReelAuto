# core/services/task_runner.py
import logging
from decouple import config
from datetime import datetime
from core.services.hikerapi_client import HikerAPIClient
from core.services.hiker_reels_processor import HikerReelsProcessor
from core.models import SearchRawResult


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
    from core.models import SearchResult, SearchRawResult
    from io import StringIO
    from django.core.files.base import ContentFile
    import csv
    from django.db import transaction

    api = HikerAPIClient(config("HIKER_API_KEY"))
    processor = HikerReelsProcessor(api)

    hashtag = _extract_first_hashtag(task.keywords)
    if not hashtag:
        raise ValueError("Не указан хэштег для задачи поиска")

    logger.warning(f"[TASK #{task.id}] 🚨 Запрос к HikerAPI будет тарифицирован (~$0.02). "
                   f"Хэштег: #{hashtag} | лимит: {task.limit} | фильтры: views>={task.views_from or 0}, "
                   f"likes>={task.likes_from or 0}, comments>={task.comments_from or 0}")

    try:
        filtered_reels, raw_reels = processor.fetch_and_filter(
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
        task.error_message = str(e)
        task.save()
        return 0

    # Сохраняем в БД через транзакцию
    try:
        with transaction.atomic():
            # Сохраняем все сырые рилсы
            raw_objects = []
            for reel_data in raw_reels:
                raw_objects.append(SearchRawResult(task=task, **reel_data))
            
            if raw_objects:
                SearchRawResult.objects.bulk_create(raw_objects, ignore_conflicts=True)
                logger.info(f"[DB] Сохранено {len(raw_objects)} raw reel(s)")

            # Сохраняем отфильтрованные рилсы
            filtered_objects = []
            for reel_data in filtered_reels:
                filtered_objects.append(SearchResult(task=task, **reel_data))
            
            if filtered_objects:
                SearchResult.objects.bulk_create(filtered_objects, ignore_conflicts=True)
                logger.info(f"[DB] Сохранено {len(filtered_objects)} filtered reel(s)")

    except Exception as e:
        logger.exception(f"[TASK #{task.id}] Ошибка при сохранении в БД: {e}")
        task.status = 'error'
        task.error_message = f"Ошибка сохранения: {str(e)}"
        task.save()
        return 0

    # Генерируем CSV
    try:
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Ссылка", "Автор", "Дата", "Описание", "Хэштеги", "Просмотры", "Лайки", "Комментарии", "Звук"])
        
        for reel in filtered_reels:
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
        
    except Exception as e:
        logger.warning(f"[CSV] Ошибка создания CSV: {e}")
        # Не критично, продолжаем

    task.status = 'done'
    task.save()

    logger.info(f"[TASK #{task.id}] Завершено. Raw: {len(raw_reels)}, Filtered: {len(filtered_reels)}")
    return len(filtered_reels)