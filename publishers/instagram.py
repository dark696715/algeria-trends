"""
النشر على إنستغرام (حساب أعمال/منشئ) عبر Graph API — عملية من خطوتين.
Instagram publisher via Graph API (two-step: create container -> publish).

متطلبات مهمة:
- حساب Instagram Business/Creator مرتبط بصفحة فيسبوك.
- الصورة/الفيديو يجب أن يكون على رابط عام (public URL) — إنستغرام يجلب الوسيط من الرابط.
- لا يمكن نشر منشور بدون وسيط (صورة/فيديو).
"""
from __future__ import annotations

import time

import requests

GRAPH = "https://graph.facebook.com/v19.0"


def is_enabled(cfg) -> bool:
    ig = cfg.get("publishers", "instagram", default={}) or {}
    return bool(ig.get("enabled"))


def publish(post, cfg, dry_run: bool = False) -> tuple[bool, str]:
    ig = cfg.get("publishers", "instagram", default={}) or {}
    ig_user_id = str(ig.get("ig_user_id", "") or "")
    token = str(ig.get("access_token", "") or "")

    if not ig_user_id or "معرّف" in ig_user_id or not token or "توكن" in token:
        return False, "إعدادات إنستغرام غير مكتملة (ig_user_id / access_token)."

    if not post.media_url:
        return False, "إنستغرام يتطلب صورة/فيديو — لا يمكن نشر نص فقط."

    caption = post.full_text(limit=2100)

    if dry_run:
        print(f"[instagram] 🧪 (تجربة) سيُنشر على {ig_user_id} بصورة:\n{post.media_url}\nالتعليق:\n{caption[:300]}...")
        return True, "dry-run"

    try:
        # 1) إنشاء حاوية الوسيط
        create = requests.post(
            f"{GRAPH}/{ig_user_id}/media",
            data={"image_url": post.media_url, "caption": caption, "access_token": token},
            timeout=60,
        )
        create.raise_for_status()
        creation_id = create.json().get("id")
        if not creation_id:
            return False, f"لم يتم إنشاء حاوية الوسيط: {create.text[:200]}"

        # مهلة قصيرة حتى تجهز الحاوية
        time.sleep(3)

        # 2) نشر الحاوية
        publish_resp = requests.post(
            f"{GRAPH}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        publish_resp.raise_for_status()
        return True, "تم النشر بنجاح"
    except requests.RequestException as e:
        detail = ""
        resp = getattr(e, "response", None)
        if resp is not None:
            detail = f" | {resp.text[:200]}"
        return False, f"خطأ إنستغرام: {e}{detail}"
