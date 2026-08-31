"""
نموذج بيانات موحّد للترند (Trend item) يُستخدم عبر كل الوحدات.
A unified data model for a trend item used across all modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional
import hashlib


@dataclass
class TrendItem:
    """عنصر ترند واحد قادم من أي مصدر."""

    source: str                       # مصدر الترند: "youtube" أو "google_trends"
    title: str                        # العنوان / الكلمة الرائجة
    url: str = ""                     # الرابط (إن وُجد)
    description: str = ""             # وصف مختصر
    thumbnail_url: str = ""          # صورة مصغّرة (للفيديو مثلاً)
    channel: str = ""                # اسم القناة / الناشر
    metric: str = ""                 # مقياس (مشاهدات، حجم بحث...)
    rank: int = 0                     # الترتيب في القائمة
    extra: dict = field(default_factory=dict)  # أي بيانات إضافية

    def unique_key(self) -> str:
        """مفتاح فريد يُستخدم لتجنّب إعادة نشر نفس الترند."""
        base = (self.url or self.title or "").strip().lower()
        raw = f"{self.source}:{base}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)
