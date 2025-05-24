# core/services/task_runner.py
from .reels_fetcher import ReelsFetcher
from core.models import SearchResult

from io import StringIO
from django.core.files.base import ContentFile
import csv


def run_search_task(task):
    fetcher = ReelsFetcher()

    hashtag = _extract_first_hashtag(task.keywords)
    if not hashtag:
        raise ValueError("Не указан хэштег для задачи поиска")

    reels = fetcher.fetch_by_hashtag(
        hashtag=hashtag,
        min_views=task.views_from or 0,
        min_likes=task.likes_from or 0,
        min_comments=task.comments_from or 0,
        date_from=task.date_from,
        date_to=task.date_to,
        limit=2
    )

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

    return len(reels)


def _extract_first_hashtag(keywords: str) -> str:
    if not keywords:
        return None
    for word in keywords.split():
        word = word.strip().strip(',')  # убираем пробелы и запятые
        if word.startswith('#'):
            return word[1:]
    return None

