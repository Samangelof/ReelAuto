import requests
import logging
from typing import Optional


logger = logging.getLogger(__name__)

class HikerAPIClient:
    BASE_URL = "https://api.hikerapi.com"
    TIMEOUT = 15

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "x-access-key": self.token,
            "accept": "application/json"
        })

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        try:
            logger.info(f"[HIKER] GET {url} | params={params}")
            response = self.session.get(url, params=params or {}, timeout=self.TIMEOUT)
            response.raise_for_status()
            logger.debug(f"[HIKER] RESPONSE: {response.status_code} | {response.text}")
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"[HIKER] HTTP ERROR {response.status_code} — {response.text}")
            raise
        except Exception as e:
            logger.exception("[HIKER] REQUEST FAILED")
            raise

    def get_user_by_id(self, user_id: int) -> dict:
        return self._get("/v1/user/by/id", {"id": user_id})

    def get_followers_chunk(self, user_id: int, max_id: Optional[str] = None) -> dict:
        return self._get("/v1/user/followers/chunk", {"user_id": user_id, "max_id": max_id})

    def get_hashtag_info(self, name: str) -> dict:
        return self._get("/v2/hashtag/by/name", {"name": name})

    def get_reels_by_hashtag(self, name: str, page_id: str | None = None) -> dict:
        params = {"name": name}
        if page_id:
            params["page_id"] = page_id

        return self._get("/v2/hashtag/medias/clips", params)



    def get_hashtag_top_clips(self, name: str, page_id: Optional[str] = None) -> dict:
        return self._get("/v2/hashtag/medias/top", {"name": name, "page_id": page_id})
