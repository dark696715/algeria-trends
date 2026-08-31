"""
جامع ترندات يوتيوب: أكثر الفيديوهات رواجاً في الجزائر (regionCode=DZ).
YouTube collector: most popular videos in Algeria via YouTube Data API v3.

الوثائق: https://developers.google.com/youtube/v3/docs/videos/list
"""
from __future__ import annotations

import requests

from core.models import TrendItem

YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def collect(cfg) -> list[TrendItem]:
    yt = cfg.get("collectors", "youtube", default={}) or {}
    if not yt.get("enabled", False):
        return []

    api_key = str(yt.get("api_key", "") or "")
    if not api_key or api_key.startswith("ضع_"):
        print("[youtube] ⚠️  لا يوجد مفتاح API صالح — تم تخطّي يوتيوب.")
        return []

    region = cfg.get("general", "region", default="DZ")
    max_results = int(yt.get("max_results", 15))

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max(1, min(max_results, 50)),
        "key": api_key,
    }
    category = yt.get("category_id")
    if category:
        params["videoCategoryId"] = str(category)

    try:
        resp = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[youtube] ❌ خطأ في الاتصال بـ YouTube API: {e}")
        return []

    items: list[TrendItem] = []
    for i, v in enumerate(data.get("items", []), start=1):
        snip = v.get("snippet", {})
        stats = v.get("statistics", {})
        vid = v.get("id", "")
        thumbs = snip.get("thumbnails", {})
        thumb = (
            thumbs.get("high")
            or thumbs.get("medium")
            or thumbs.get("default")
            or {}
        ).get("url", "")

        views = stats.get("viewCount")
        metric = ""
        if views and str(views).isdigit():
            metric = f"{int(views):,} مشاهدة"

        items.append(
            TrendItem(
                source="youtube",
                title=(snip.get("title", "") or "").strip(),
                url=f"https://www.youtube.com/watch?v={vid}" if vid else "",
                description=(snip.get("description", "") or "")[:280],
                thumbnail_url=thumb,
                channel=snip.get("channelTitle", ""),
                metric=metric,
                rank=i,
            )
        )

    print(f"[youtube] ✅ تم جمع {len(items)} فيديو رائج (المنطقة={region}).")
    return items
