import re
from typing import Optional

import requests

from app.config import get_logger
from app.config.conf import youtube_url

logger = get_logger("[utils/api_utils]")


def iso8601_duration_to_seconds(duration: Optional[str]) -> Optional[int]:
    """
    Convert ISO 8601 duration (e.g. 'PT1H2M10S', 'PT3M20S') to seconds.
    Returns None if input is falsy or can't be parsed.
    """
    if not duration:
        return None
    try:
        hours = minutes = seconds = 0
        m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
        if not m:
            return None
        h, mi, s = m.groups()
        hours = int(h) if h else 0
        minutes = int(mi) if mi else 0
        seconds = int(s) if s else 0
        return hours * 3600 + minutes * 60 + seconds
    except Exception:
        return None


def fetch_youtube_video_metadata(video_id: str, api_key: str) -> Optional[dict]:
    """
    Returns a dict with normalized fields or None if not found/error.
    Keeps errors internal and returns None so callers can decide.
    """
    try:
        if not video_id:
            logger.error("No Video Id provide")
            return None

        url = youtube_url
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": api_key,
        }
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            logger.warning(
                "YouTube API returned non-200 for %s: %s", video_id, resp.status_code
            )
            return None

        data = resp.json()
        items = data.get("items") or []
        if not items:
            logger.info("YouTube API returned no items for %s", video_id)
            return None

        info = items[0]
        snippet = info.get("snippet", {})
        content = info.get("contentDetails", {})
        statistics = info.get("statistics", {})

        return {
            "video_id": video_id,
            "etag": info.get("etag"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "thumbnail_url": (snippet.get("thumbnails") or {})
            .get("high", {})
            .get("url"),
            "duration_iso8601": content.get("duration"),
            "duration_seconds": iso8601_duration_to_seconds(content.get("duration")),
            "view_count": (
                int(statistics.get("viewCount"))
                if statistics.get("viewCount")
                else None
            ),
            "like_count": (
                int(statistics.get("likeCount"))
                if statistics.get("likeCount")
                else None
            ),
            "comment_count": (
                int(statistics.get("commentCount"))
                if statistics.get("commentCount")
                else None
            ),
        }
    except Exception as exc:
        logger.error("Error fetching YouTube metadata for %s: %s", video_id, str(exc))
        return None
