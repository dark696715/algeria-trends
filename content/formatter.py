"""
يحوّل قائمة الترندات إلى منشورات عربية جاهزة للنشر.
Turns TrendItems into ready-to-post content, tailored per platform.

- منشور مجمّع (digest): قائمة بأبرز الترندات — مناسب لتيليغرام وفيسبوك.
- منشور فردي (item): ترند واحد مع صورة مصغّرة — مناسب لإنستغرام.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.models import TrendItem

# الحد الأقصى التقريبي لأطوال النصوص حسب المنصة
LIMITS = {
    "telegram": 4000,
    "facebook": 60000,
    "instagram": 2100,
    "tiktok": 2100,
    "generic": 4000,
}


@dataclass
class Post:
    """منشور جاهز للإرسال إلى ناشر معيّن."""
    text: str
    hashtags: list[str] = field(default_factory=list)
    media_url: str = ""          # صورة/فيديو مصغّر إن وُجد
    link: str = ""               # رابط رئيسي إن وُجد

    def full_text(self, limit: int = 4000) -> str:
        tags = " ".join(self.hashtags)
        body = self.text
        if tags:
            body = f"{body}\n\n{tags}"
        return body[:limit].rstrip()


def _hashtags(cfg) -> list[str]:
    return list(cfg.get("content", "hashtags", default=[]) or [])


def _source_label(source: str) -> str:
    return {
        "youtube": "📺 يوتيوب",
        "google_trends": "🔎 بحث Google",
        "tiktok": "🎵 تيك توك",
    }.get(source, "🔥 ترند")


def format_digest(trends: list[TrendItem], cfg, platform: str = "generic") -> Post:
    """منشور واحد يجمع أبرز الترندات في قائمة مرقّمة."""
    intro = cfg.get("content", "intro_line", default="🔥 أبرز الترندات في الجزائر الآن:")
    include_links = bool(cfg.get("content", "include_links", default=True))
    signature = cfg.get("content", "brand_signature", default="") or ""

    lines = [intro, ""]
    for t in trends:
        label = _source_label(t.source)
        line = f"{t.rank}. {t.title}"
        extras = []
        if t.metric:
            extras.append(t.metric)
        if t.channel:
            extras.append(t.channel)
        if extras:
            line += f"  ({' • '.join(extras)})"
        lines.append(f"{label} — {line}")
        if include_links and t.url:
            lines.append(f"    🔗 {t.url}")
        lines.append("")

    if signature:
        lines.append(signature)

    text = "\n".join(lines).rstrip()
    limit = LIMITS.get(platform, LIMITS["generic"])
    return Post(
        text=text[:limit],
        hashtags=_hashtags(cfg),
        media_url=next((t.thumbnail_url for t in trends if t.thumbnail_url), ""),
    )


def format_item(trend: TrendItem, cfg, platform: str = "generic") -> Post:
    """منشور فردي لترند واحد (مفيد لإنستغرام حيث يلزم وسيط لكل منشور)."""
    include_links = bool(cfg.get("content", "include_links", default=True))
    signature = cfg.get("content", "brand_signature", default="") or ""
    label = _source_label(trend.source)

    parts = [f"{label}", "", f"🔥 {trend.title}"]
    if trend.metric:
        parts.append(f"📊 {trend.metric}")
    if trend.channel:
        parts.append(f"👤 {trend.channel}")
    if trend.description:
        parts.append("")
        parts.append(trend.description[:400])
    if include_links and trend.url and platform != "instagram":
        # انستغرام لا يدعم الروابط القابلة للنقر في التعليق
        parts.append("")
        parts.append(f"🔗 {trend.url}")
    if signature:
        parts.append("")
        parts.append(signature)

    text = "\n".join(parts).rstrip()
    limit = LIMITS.get(platform, LIMITS["generic"])
    return Post(
        text=text[:limit],
        hashtags=_hashtags(cfg),
        media_url=trend.thumbnail_url,
        link=trend.url,
    )
