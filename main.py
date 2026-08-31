#!/usr/bin/env python3
"""
المنسّق الرئيسي لـ workflow جمع ترندات الجزائر ونشرها تلقائياً.
Main orchestrator: collect Algeria trends -> format -> publish to all platforms.

الاستخدام:
    python main.py                 # يشتغل حسب config.json
    python main.py --dry-run       # تجربة بدون نشر فعلي
    python main.py --config my.json

الفكرة العامة:
    1) جمع الترندات من المصادر المفعّلة (يوتيوب + Google Trends).
    2) استبعاد ما سبق نشره (تجنّب التكرار).
    3) توليد منشور مجمّع + منشورات فردية.
    4) النشر على كل المنصات المفعّلة.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from core.config import Config
from core.state import SeenStore
from collectors import youtube, google_trends
from content import formatter
from publishers import ALL as PUBLISHERS


def setup_logging(log_file: str) -> None:
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def collect_all(cfg) -> list:
    """يجمع الترندات من كل المصادر المفعّلة ويعيد قائمة موحّدة."""
    trends = []
    trends += youtube.collect(cfg)
    trends += google_trends.collect(cfg)
    # إعادة ترقيم موحّدة بعد الدمج
    for i, t in enumerate(trends, start=1):
        t.rank = i
    return trends


def run_once(config_path: str = "config.json", force_dry_run: bool = False) -> int:
    cfg = Config.load(config_path)
    log_file = cfg.get("general", "log_file", default="logs/workflow.log")
    setup_logging(log_file)
    log = logging.getLogger("workflow")

    dry_run = force_dry_run or cfg.is_dry_run()
    log.info("🚀 بدء التشغيل | وضع التجربة=%s", dry_run)

    # 1) الجمع
    trends = collect_all(cfg)
    if not trends:
        log.warning("لم يتم جمع أي ترند. تأكّد من المفاتيح والاتصال. إنهاء.")
        return 0
    log.info("📥 إجمالي الترندات المجمّعة: %d", len(trends))

    # 2) استبعاد المكرّر
    state_file = cfg.get("general", "state_file", default="state/seen.json")
    store = SeenStore(state_file)
    new_trends = store.filter_new(trends)
    if not new_trends:
        log.info("كل الترندات منشورة مسبقاً — لا جديد. إنهاء.")
        return 0

    max_n = int(cfg.get("general", "max_trends_per_run", default=8))
    selected = new_trends[:max_n]
    for i, t in enumerate(selected, start=1):
        t.rank = i
    log.info("✨ ترندات جديدة مختارة للنشر: %d", len(selected))

    # 3) توليد المنشورات + 4) النشر لكل منصة مفعّلة
    any_success = False
    for name, module in PUBLISHERS.items():
        if not module.is_enabled(cfg):
            continue

        # إنستغرام يحتاج وسيطاً لكل منشور → ننشر أول ترند يملك صورة مصغّرة
        if name == "instagram":
            item = next((t for t in selected if t.thumbnail_url), None)
            if not item:
                log.warning("[%s] لا يوجد ترند بصورة صالحة — تخطّي.", name)
                continue
            post = formatter.format_item(item, cfg, platform=name)
        else:
            post = formatter.format_digest(selected, cfg, platform=name)

        ok, msg = module.publish(post, cfg, dry_run=dry_run)
        level = logging.INFO if ok else logging.ERROR
        log.log(level, "[%s] %s → %s", name, "✅" if ok else "❌", msg)
        any_success = any_success or ok

    # 5) تسجيل ما نُشر لتجنّب تكراره لاحقاً (فقط لو نجح نشر واحد على الأقل وليس تجربة)
    if any_success and not dry_run:
        for t in selected:
            store.mark(t.unique_key())
        store.save()
        log.info("💾 تم حفظ حالة %d ترند لتجنّب التكرار.", len(selected))

    log.info("🏁 انتهى التشغيل.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Algeria Trends Auto-Publisher")
    parser.add_argument("--config", default="config.json", help="مسار ملف الإعدادات")
    parser.add_argument("--dry-run", action="store_true", help="تجربة بدون نشر فعلي")
    args = parser.parse_args()
    try:
        return run_once(args.config, force_dry_run=args.dry_run)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except KeyboardInterrupt:
        print("\nتم الإيقاف.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
