"""
النشر على صفحة فيسبوك عبر Graph API.
Facebook Page publisher via Graph API.

مهم: لا يمكن النشر على الملفات الشخصية — فقط على الصفحات (Pages).
يتطلب: page_id + page_access_token (توكن وصول صفحة طويل الأمد).
"""
from __future__ import annotations

import requests

GRAPH = "https://graph.facebook.com/v19.0"


def is_enabled(cfg) -> bool:
    fb = cfg.get("publishers", "facebook", default={}) or {}
    return bool(fb.get("enabled"))


def publish(post, cfg, dry_run: bool = False) -> tuple[bool, str]:
    fb = cfg.get("publishers", "facebook", default={}) or {}
    page_id = str(fb.get("page_id", "") or "")
    token = str(fb.get("page_access_token", "") or "")

    if not page_id or "معرّف" in page_id or not token or "توكن" in token:
        return False, "إعدادات فيسبوك غير مكتملة (page_id / page_access_token)."

    text = post.full_text(limit=60000)

    if dry_run:
        kind = "صورة + نص" if post.media_url else "نص/رابط"
        print(f"[facebook] 🧪 (تجربة) سيُنشر ({kind}) على الصفحة {page_id}:\n{text[:300]}...")
        return True, "dry-run"

    try:
        if post.media_url:
            url = f"{GRAPH}/{page_id}/photos"
            payload = {"url": post.media_url, "caption": text, "access_token": token}
        else:
            url = f"{GRAPH}/{page_id}/feed"
            payload = {"message": text, "access_token": token}
            if post.link:
                payload["link"] = post.link

        r = requests.post(url, data=payload, timeout=30)
        r.raise_for_status()
        return True, "تم النشر بنجاح"
    except requests.RequestException as e:
        detail = ""
        resp = getattr(e, "response", None)
        if resp is not None:
            detail = f" | {resp.text[:200]}"
        return False, f"خطأ فيسبوك: {e}{detail}"
