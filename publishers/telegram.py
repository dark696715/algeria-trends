"""
النشر على تيليغرام عبر Bot API (مجاني تماماً).
Telegram publisher via the free Bot API.

الإعداد: أنشئ بوتاً عبر @BotFather، ثم أضِف البوت مشرفاً في قناتك.
"""
from __future__ import annotations

import requests

API = "https://api.telegram.org/bot{token}/{method}"


def is_enabled(cfg) -> bool:
    tg = cfg.get("publishers", "telegram", default={}) or {}
    return bool(tg.get("enabled"))


def publish(post, cfg, dry_run: bool = False) -> tuple[bool, str]:
    tg = cfg.get("publishers", "telegram", default={}) or {}
    token = str(tg.get("bot_token", "") or "")
    chat_id = str(tg.get("chat_id", "") or "")

    if not token or token.startswith("ضع_") or not chat_id or "اسم_قناتك" in chat_id:
        return False, "إعدادات تيليغرام غير مكتملة (bot_token / chat_id)."

    text = post.full_text(limit=4096)

    if dry_run:
        print(f"[telegram] 🧪 (تجربة) سيتم إرسال هذا المنشور:\n{'-'*40}\n{text}\n{'-'*40}")
        return True, "dry-run"

    try:
        # صورة مع تعليق إذا كان التعليق قصيراً (حد تيليغرام للتعليق 1024 حرفاً)
        if post.media_url and len(text) <= 1024:
            url = API.format(token=token, method="sendPhoto")
            payload = {"chat_id": chat_id, "photo": post.media_url, "caption": text}
        else:
            url = API.format(token=token, method="sendMessage")
            payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": False}

        r = requests.post(url, data=payload, timeout=30)
        r.raise_for_status()
        ok = bool(r.json().get("ok"))
        return ok, ("تم النشر بنجاح" if ok else f"رد غير متوقع: {r.text[:200]}")
    except requests.RequestException as e:
        detail = ""
        resp = getattr(e, "response", None)
        if resp is not None:
            detail = f" | {resp.text[:200]}"
        return False, f"خطأ تيليغرام: {e}{detail}"
