import requests
import logging
from datetime import datetime
from .hikerapi_client import HikerAPIClient
from xml.etree import ElementTree as ET


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



def extract_sound_url(media: dict) -> str:
    if "progressive_download_url" in media:
        return media["progressive_download_url"]

    dash_xml = (
        media.get("music_info", {})
        .get("music_asset_info", {})
        .get("dash_manifest")
    )

    if dash_xml:
        try:
            root = ET.fromstring(dash_xml)
            base_url = root.find(".//{urn:mpeg:dash:schema:mpd:2011}BaseURL")
            if base_url is not None and base_url.text:
                return base_url.text
        except Exception as e:
            logger.warning(f"[PARSER] ошибка при парсинге dash_manifest: {e}")

    return ""


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
            sound_url = extract_sound_url(media)


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