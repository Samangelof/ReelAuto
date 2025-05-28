# import logging
# from instagrapi import Client
# from datetime import datetime
# from decouple import config

# logger = logging.getLogger(__name__)

# class ReelsFetcher:
#     def __init__(self):
#         logger.info("Инициализация ReelsFetcher")
#         self.client = Client()
#         self.client.login(config('IG_USERNAME'), config('IG_PASSWORD'))
#         logger.info("Успешный логин в Instagram")

#     def fetch_by_hashtag(self, hashtag, min_views=0, min_likes=0, min_comments=0,
#                          date_from=None, date_to=None, limit=50):
#         logger.info(f"Поиск по хэштегу #{hashtag}, лимит={limit}, "
#                     f"мин. просмотров={min_views}, лайков={min_likes}, комментов={min_comments}, "
#                     f"дата от={date_from}, до={date_to}")

#         try:
#             medias = self.client.hashtag_medias_v1(hashtag, amount=limit, tab_key="clips")
#             logger.info(f"Получено {len(medias)} медиа из Instagram")
#         except Exception as e:
#             logger.error(f"Ошибка при запросе хэштега: {e}")
#             return []

#         results = []
#         for media in medias:
#             data = media.dict()

#             # logger.debug("Media raw data: %s", str(data)[:2000])
#             logger.debug("Media author: %s | media_type: %s", data.get("user", {}).get("username"), data.get("media_type"))

#             if not data.get("video_url"):
#                 logger.debug("Пропуск: нет video_url")
#                 continue

#             # Метрики
#             if data.get("view_count", 0) < min_views:
#                 logger.debug("Пропуск: мало просмотров")
#                 continue
#             if data.get("like_count", 0) < min_likes:
#                 logger.debug("Пропуск: мало лайков")
#                 continue
#             if data.get("comment_count", 0) < min_comments:
#                 logger.debug("Пропуск: мало комментариев")
#                 continue

#             # Дата
#             created = data.get("taken_at")
#             if not created:
#                 logger.debug("Пропуск: нет даты публикации")
#                 continue

#             if date_from and created.date() < date_from:
#                 logger.debug("Пропуск: слишком старая дата")
#                 continue

#             if date_to and created.date() > date_to:
#                 logger.debug("Пропуск: слишком новая дата")
#                 continue

#             results.append({
#                 "video_url": data.get("video_url"),
#                 "author_username": data.get("user", {}).get("username"),
#                 "published_at": created,
#                 "description": data.get("caption_text", ""),
#                 "hashtags": " ".join(data.get("hashtags", [])),
#                 "views": data.get("view_count", 0),
#                 "likes": data.get("like_count", 0),
#                 "comments": data.get("comment_count", 0),
#                 "sound_url": data.get("audio", {}).get("audio_url", ""),
#             })

#         logger.info(f"Итого прошло фильтры: {len(results)}")
#         return results



# Hiker
# core/services/reels_fetcher.py
import requests
import logging
from datetime import datetime
from .hikerapi_client import HikerAPIClient


logger = logging.getLogger(__name__)


def safe_truncate_data(data: dict) -> dict:
    """Безопасно обрезает данные до лимитов БД"""
    return {
        "video_url": (data.get("video_url") or "")[:2048],
        "author_username": (data.get("author_username") or "")[:500],
        "published_at": data.get("published_at"),
        "description": (data.get("description") or "")[:5000],
        "hashtags": (data.get("hashtags") or "")[:2000],
        "views": data.get("views", 0),
        "likes": data.get("likes", 0),
        "comments": data.get("comments", 0),
        "sound_url": (data.get("sound_url") or "")[:2048],
    }

class HikerReelsProcessor:
    def __init__(self, api_client: HikerAPIClient):
        self.api = api_client

    def _parse_reel_data(self, raw_item: dict) -> dict | None:
        """Парсит один элемент reel в унифицированный формат"""
        try:
            media = raw_item.get("media", {})
            if not media:
                logger.warning("[PARSER] пропущено: нет блока 'media'")
                return None

            caption = media.get("caption", {})
            description = caption.get("text", "")
            hashtags = [w for w in description.split() if w.startswith("#")]
            hashtags_str = " ".join(hashtags)

            user = media.get("user", {})
            video_versions = media.get("video_versions", [])
            video_url = video_versions[0]["url"] if video_versions else ""
            sound_url = media.get("progressive_download_url") or ""

            taken_at = media.get("taken_at")
            published_at = datetime.fromtimestamp(taken_at).date() if taken_at else None

            raw_data = {
                "video_url": video_url,
                "author_username": user.get("username", ""),
                "published_at": published_at,
                "description": description,
                "hashtags": hashtags_str,
                "views": media.get("play_count", 0),
                "likes": media.get("like_count", 0),
                "comments": media.get("comment_count", 0),
                "sound_url": sound_url,
            }
            
            # Применяем безопасную обрезку
            return safe_truncate_data(raw_data)
            
        except Exception as e:
            logger.warning(f"[PARSER] ошибка при парсинге reel: {e}")
            return None

    def _passes_filters(self, reel_data: dict, min_views: int, min_likes: int, 
                       min_comments: int, date_from, date_to) -> bool:
        """Проверяет, проходит ли reel все фильтры"""
        if reel_data["views"] < min_views:
            logger.info(f"[FILTER] пропущено: views={reel_data['views']} < {min_views}")
            return False
        if reel_data["likes"] < min_likes:
            logger.info(f"[FILTER] пропущено: likes={reel_data['likes']} < {min_likes}")
            return False
        if reel_data["comments"] < min_comments:
            logger.info(f"[FILTER] пропущено: comments={reel_data['comments']} < {min_comments}")
            return False
        if date_from and reel_data["published_at"] and reel_data["published_at"] < date_from:
            logger.info(f"[FILTER] пропущено: {reel_data['published_at']} < {date_from}")
            return False
        if date_to and reel_data["published_at"] and reel_data["published_at"] > date_to:
            logger.info(f"[FILTER] пропущено: {reel_data['published_at']} > {date_to}")
            return False
        return True

    def fetch_and_filter(
        self,
        hashtag: str,
        *,
        min_views=0,
        min_likes=0,
        min_comments=0,
        date_from=None,
        date_to=None,
        limit=5
    ) -> tuple[list[dict], list[dict]]:
        """Возвращает (filtered_reels, raw_reels)"""
        response = self.api.get_reels_by_hashtag(hashtag)
        sections = response.get("response", {}).get("sections", [])
        if not sections:
            logger.warning("[FILTER] Нет секций в ответе HikerAPI")
            return [], []

        items = (
            sections[0]
            .get("layout_content", {})
            .get("one_by_two_item", {})
            .get("clips", {})
            .get("items", [])
        )

        raw_reels = []
        filtered_reels = []

        for raw_item in items:
            # Парсим данные один раз
            reel_data = self._parse_reel_data(raw_item)
            if not reel_data:
                continue

            # Сохраняем в raw_reels
            raw_reels.append(reel_data)

            # Проверяем фильтры
            if self._passes_filters(reel_data, min_views, min_likes, min_comments, date_from, date_to):
                filtered_reels.append(reel_data)
                
                if len(filtered_reels) >= limit:
                    break

        logger.info(f"[FETCH] Обработано: {len(raw_reels)} raw, {len(filtered_reels)} filtered")
        return filtered_reels, raw_reels


# class ReelsFetcher:
#     def __init__(self):
#         self.token = config("HIKER_API_KEY")
#         self.base_url = "https://api.hikerapi.com/v2"
#         self.headers = {
#             "x-access-key": self.token,
#             "accept": "application/json"
#         }

#     def fetch_by_hashtag(self, hashtag, min_views=0, min_likes=0, min_comments=0,
#                          date_from=None, date_to=None, limit=50):
#         url = f"{self.base_url}/reels/by/hashtag"
#         params = {
#             "hashtag": hashtag,
#             "min_views": min_views,
#             "min_likes": min_likes,
#             "min_comments": min_comments,
#             "date_from": str(date_from) if date_from else None,
#             "date_to": str(date_to) if date_to else None,
#             "limit": limit
#         }

#         logger.info(f"[HIKER] GET {url} params={params}")
#         try:
#             resp = requests.get(url, headers=self.headers,
#                                 params=params, timeout=15)
#             resp.raise_for_status()
#         except requests.HTTPError as e:
#             logger.error(f"HIKERAPI ERROR: {resp.status_code} - {resp.text}")
#             if resp.status_code == 402:
#                 raise Exception("Нет доступа — ошибка оплаты HikerAPI.")
#             raise
#         except Exception as e:
#             logger.exception("Ошибка соединения с HikerAPI")
#             raise

#         data = resp.json().get("data", [])
#         logger.info(f"[HIKER] Получено {len(data)} reels")

#         results = []
#         for r in data:
#             results.append({
#                 "video_url": r.get("video_url"),
#                 "author_username": r.get("author_username"),
#                 "published_at": datetime.fromisoformat(r.get("published_at")),
#                 "description": r.get("description", ""),
#                 "hashtags": " ".join(r.get("hashtags") or []),
#                 "views": r.get("views", 0),
#                 "likes": r.get("likes", 0),
#                 "comments": r.get("comments", 0),
#                 "sound_url": r.get("sound_url", ""),
#             })
#         return results
