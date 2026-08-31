"""
جامع ترندات Google Trends للجزائر (بديل موثوق ومجاني عن TikTok الذي لا يوفّر API رسمياً).
Google Trends collector for Algeria — a reliable free proxy for "what's trending".

الطريقة الأساسية: قراءة خلاصة RSS اليومية للترندات.
الطريقة الاحتياطية: مكتبة pytrends (اختيارية) إن كانت مثبّتة.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from core.models import TrendItem

DAILY_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
HT_NS = "{https://trends.google.com/trends/trendingsearches/daily}"


def _from_rss(geo: str, max_results: int) -> list[TrendItem]:
    url = DAILY_RSS.format(geo=geo)
    try:
        resp = requests.get(
            url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; TrendsBot/1.0)"}
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.RequestException, ET.ParseError) as e:
        print(f"[google_trends] ⚠️  تعذّرت قراءة RSS: {e}")
        return []

    items: list[TrendItem] = []
    for i, item in enumerate(root.iterfind(".//item"), start=1):
        title_el = item.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue

        traffic_el = item.find(f"{HT_NS}approx_traffic")
        metric = (traffic_el.text or "").strip() if traffic_el is not None else ""

        news_url, news_title = "", ""
        news = item.find(f"{HT_NS}news_item")
        if news is not None:
            u = news.find(f"{HT_NS}news_item_url")
            t = news.find(f"{HT_NS}news_item_title")
            news_url = (u.text or "").strip() if u is not None else ""
            news_title = (t.text or "").strip() if t is not None else ""

        items.append(
            TrendItem(
                source="google_trends",
                title=title,
                url=news_url or f"https://www.google.com/search?q={requests.utils.quote(title)}",
                description=news_title,
                metric=(f"{metric} عملية بحث" if metric else ""),
                rank=i,
            )
        )
        if len(items) >= max_results:
            break
    return items


def _from_pytrends(geo: str, max_results: int) -> list[TrendItem]:
    """طريقة احتياطية عبر pytrends إن كانت مثبّتة."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        return []
    try:
        py = TrendReq(hl="ar", tz=60)
        df = py.realtime_trending_searches(pn=geo)
        titles = df["title"].head(max_results).tolist() if df is not None else []
    except Exception as e:  # pytrends قد يرمي أخطاء متنوعة
        print(f"[google_trends] ⚠️  pytrends غير متاح لهذه المنطقة: {e}")
        return []

    items = []
    for i, title in enumerate(titles, start=1):
        title = str(title).strip()
        if not title:
            continue
        items.append(
            TrendItem(
                source="google_trends",
                title=title,
                url=f"https://www.google.com/search?q={requests.utils.quote(title)}",
                rank=i,
            )
        )
    return items


def collect(cfg) -> list[TrendItem]:
    gt = cfg.get("collectors", "google_trends", default={}) or {}
    if not gt.get("enabled", False):
        return []

    geo = gt.get("geo", "DZ")
    max_results = int(gt.get("max_results", 15))

    items = _from_rss(geo, max_results)
    if not items:
        print("[google_trends] ℹ️  لا نتائج من RSS — تجربة pytrends (إن وُجد).")
        items = _from_pytrends(geo, max_results)

    print(f"[google_trends] ✅ تم جمع {len(items)} ترند (geo={geo}).")
    return items
