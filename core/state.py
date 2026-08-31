"""
إدارة حالة "ما تم نشره سابقاً" لتجنّب تكرار نفس الترند.
Manages a small JSON cache of already-published trend keys to avoid duplicates.
"""
from __future__ import annotations

import json
import os
import time
from typing import Iterable


class SeenStore:
    def __init__(self, path: str = "state/seen.json", ttl_days: int = 7):
        self.path = path
        self.ttl_seconds = ttl_days * 24 * 3600
        self._seen: dict[str, float] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._seen = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._seen = {}
        self._prune()

    def _prune(self) -> None:
        now = time.time()
        self._seen = {
            k: ts for k, ts in self._seen.items()
            if now - ts < self.ttl_seconds
        }

    def is_seen(self, key: str) -> bool:
        return key in self._seen

    def mark(self, key: str) -> None:
        self._seen[key] = time.time()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._seen, f, ensure_ascii=False, indent=2)

    def filter_new(self, items: Iterable) -> list:
        """يعيد فقط العناصر التي لم تُنشر من قبل."""
        return [it for it in items if not self.is_seen(it.unique_key())]
