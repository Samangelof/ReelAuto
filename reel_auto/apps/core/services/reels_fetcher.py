import logging
from instagrapi import Client
from datetime import datetime
from decouple import config

logger = logging.getLogger(__name__)

class ReelsFetcher:
    def __init__(self):
        logger.info("Инициализация ReelsFetcher")
        self.client = Client()
        self.client.login(config('IG_USERNAME'), config('IG_PASSWORD'))
        logger.info("Успешный логин в Instagram")

    def fetch_by_hashtag(self, hashtag, min_views=0, min_likes=0, min_comments=0,
                         date_from=None, date_to=None, limit=50):
        logger.info(f"Поиск по хэштегу #{hashtag}, лимит={limit}, "
                    f"мин. просмотров={min_views}, лайков={min_likes}, комментов={min_comments}, "
                    f"дата от={date_from}, до={date_to}")

        try:
            medias = self.client.hashtag_medias_v1(hashtag, amount=limit, tab_key="clips")
            logger.info(f"Получено {len(medias)} медиа из Instagram")
        except Exception as e:
            logger.error(f"Ошибка при запросе хэштега: {e}")
            return []

        results = []
        for media in medias:
            data = media.dict()

            if not data.get("video_url"):
                logger.debug("Пропуск: нет video_url")
                continue

            # Метрики
            if data.get("view_count", 0) < min_views:
                logger.debug("Пропуск: мало просмотров")
                continue
            if data.get("like_count", 0) < min_likes:
                logger.debug("Пропуск: мало лайков")
                continue
            if data.get("comment_count", 0) < min_comments:
                logger.debug("Пропуск: мало комментариев")
                continue

            # Дата
            created = data.get("taken_at")
            if not created:
                logger.debug("Пропуск: нет даты публикации")
                continue

            if date_from and created.date() < date_from:
                logger.debug("Пропуск: слишком старая дата")
                continue
            
            if date_to and created.date() > date_to:
                logger.debug("Пропуск: слишком новая дата")
                continue

            results.append({
                "video_url": data.get("video_url"),
                "author_username": data.get("user", {}).get("username"),
                "published_at": created,
                "description": data.get("caption_text", ""),
                "hashtags": " ".join(data.get("hashtags", [])),
                "views": data.get("view_count", 0),
                "likes": data.get("like_count", 0),
                "comments": data.get("comment_count", 0),
                "sound_url": data.get("audio", {}).get("audio_url", ""),
            })

        logger.info(f"Итого прошло фильтры: {len(results)}")
        return results
