"""
النشر على تيك توك عبر Content Posting API.
TikTok publisher via the Content Posting API (PULL_FROM_URL flow).

⚠️ ملاحظات مهمة:
- تيك توك يتطلب فيديو حقيقياً (لا يمكن نشر نص/صورة فقط كمنشور عادي).
- يتطلب تطبيقاً معتمداً من TikTok for Developers مع صلاحية video.publish.
- الرابط (video_url) يجب أن يكون على نطاق موثّق (verified domain) لدى تيك توك.
لذلك تعمل هذه الوحدة فقط عندما تُوفّر رابط فيديو صالحاً في الترند.
"""
from __future__ import annotations

import requests

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"


def is_enabled(cfg) -> bool:
    tt = cfg.get("publishers", "tiktok", default={}) or {}
    return bool(tt.get("enabled"))


def publish(post, cfg, dry_run: bool = False) -> tuple[bool, str]:
    tt = cfg.get("publishers", "tiktok", default={}) or {}
    token = str(tt.get("access_token", "") or "")

    if not token or "توكن" in token:
        return False, "إعدادات تيك توك غير مكتملة (access_token)."

    # نبحث عن رابط فيديو صالح: إمّا في post.extra أو media_url إن كان فيديو
    video_url = ""
    if isinstance(getattr(post, "extra", None), dict):
        video_url = post.extra.get("video_url", "")
    if not video_url and post.media_url and post.media_url.lower().endswith((".mp4", ".mov")):
        video_url = post.media_url

    if not video_url:
        return False, "تيك توك يتطلب رابط فيديو (.mp4) — لا يوجد فيديو صالح في هذا الترند."

    caption = post.full_text(limit=2100)

    if dry_run:
        print(f"[tiktok] 🧪 (تجربة) سيُرفع فيديو من: {video_url}\nالتعليق: {caption[:200]}...")
        return True, "dry-run"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    body = {
        "post_info": {
            "title": caption[:150],
            "privacy_level": "SELF_ONLY",  # ابدأ خاصاً للاختبار ثم غيّرها لـ PUBLIC_TO_EVERYONE
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_url,
        },
    }

    try:
        r = requests.post(INIT_URL, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        if data.get("error", {}).get("code") not in (None, "ok"):
            return False, f"رفض تيك توك الطلب: {data.get('error')}"
        return True, "تم بدء رفع الفيديو بنجاح"
    except requests.RequestException as e:
        detail = ""
        resp = getattr(e, "response", None)
        if resp is not None:
            detail = f" | {resp.text[:200]}"
        return False, f"خطأ تيك توك: {e}{detail}"
