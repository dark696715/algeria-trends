"""
تحميل وقراءة ملف الإعدادات config.json.
Loads and validates config.json (falls back to config.example.json).
"""
from __future__ import annotations

import json
import os
from typing import Any


class Config:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        # إن لم يوجد config.json، جرّب النسخة المثال للسماح بالتجربة
        if not os.path.exists(path):
            example = "config.example.json"
            if os.path.exists(example):
                print(f"[config] لم يُعثر على {path} — سيتم استخدام {example} (وضع التجربة).")
                path = example
            else:
                raise FileNotFoundError(
                    f"لم يُعثر على ملف الإعدادات: {path}. "
                    f"انسخ config.example.json إلى config.json واملأ القيم."
                )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def get(self, *keys: str, default: Any = None) -> Any:
        """قراءة قيمة متداخلة: cfg.get('publishers', 'telegram', 'bot_token')."""
        node: Any = self._data
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    @property
    def raw(self) -> dict:
        return self._data

    def is_dry_run(self) -> bool:
        return bool(self.get("general", "dry_run", default=True))
