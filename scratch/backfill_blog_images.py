#!/usr/bin/env python3
"""
Give existing blog posts their own featured image, a few per day (newest posts first).

A post still needs one while its image is a copy of a store product photo
(e.g. articles/SpecialMangoBig_<uuid>.webp). Posts are only updated when a new image was
actually generated — the product-photo fallback never overwrites anything.

Usage:
  export SHOPIFY_ACCESS_TOKEN=shpat_xxx CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=...
  python3 scratch/backfill_blog_images.py --status
  python3 scratch/backfill_blog_images.py --limit 15
"""

from __future__ import annotations

import argparse
import re
import time
import urllib.parse

import arham_keyword_content_engine as engine
from blog_image_generator import featured_image

PRODUCT_PHOTO_STEMS = tuple(
    urllib.parse.urlparse(p["image"]).path.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
    for p in engine.PRODUCTS.values()
)
PRODUCTS_BY_HANDLE = {p["handle"]: p for p in engine.PRODUCTS.values()}
PRODUCT_LINK_RE = re.compile(r"/products/([a-z0-9-]+)")
ANGLE_RE = re.compile(r"-(heritage|health|buy|pairing|craft)(?:-|$)")
TITLE_NOISE_RE = re.compile(
    r"^(buy|authentic)\s+|\s+(from divyaprabha foods|homemade achar|gujarati homemade achar guide)$",
    re.IGNORECASE,
)


def needs_new_image(article: dict) -> bool:
    src = ((article.get("image") or {}).get("src") or "").lower()
    if not src:
        return True
    name = urllib.parse.urlparse(src).path.rsplit("/", 1)[-1]
    return name.startswith(PRODUCT_PHOTO_STEMS)


def keyword_from_title(title: str) -> str:
    kw = re.split(r"\s*[:|—–]\s*", title, maxsplit=1)[0]
    return TITLE_NOISE_RE.sub("", kw).strip() or title


def product_for(article: dict, keyword: str) -> dict:
    for handle in PRODUCT_LINK_RE.findall(article.get("body_html") or ""):
        if handle in PRODUCTS_BY_HANDLE:
            return PRODUCTS_BY_HANDLE[handle]
    return engine.map_product(None, keyword)


def list_articles() -> list[dict]:
    articles, since_id = [], 0
    for _ in range(40):
        arts = engine.api(
            "GET",
            f"blogs/{engine.BLOG_ID}/articles.json?limit=250&published_status=any"
            f"&fields=id,handle,title,image,body_html,published_at&since_id={since_id}",
        ).get("articles") or []
        if not arts:
            break
        articles.extend(arts)
        since_id = max(a["id"] for a in arts)
        if len(arts) < 250:
            break
        time.sleep(0.4)
    return articles


def pending_articles() -> list[dict]:
    pending = [a for a in list_articles() if needs_new_image(a)]
    pending.sort(key=lambda a: a.get("published_at") or "", reverse=True)
    return pending


def backfill(limit: int):
    engine.require_token()
    pending = pending_articles()
    print(f"{len(pending)} post(s) still use a product photo; updating up to {limit} today.")
    done = 0
    for art in pending:
        if done >= limit:
            break
        keyword = keyword_from_title(art.get("title") or art["handle"])
        prod = product_for(art, keyword)
        m = ANGLE_RE.search(art["handle"])
        angle = m.group(1) if m else engine.pick_angle(keyword, art["handle"])
        print(f"→ {art['handle']} | {keyword} | {angle} | {prod['handle']}")
        image = featured_image(
            keyword, angle, prod["handle"], prod["image"], art["handle"], f"{keyword} — {prod['name']}"
        )
        if "attachment" not in image:
            print("   ⏭  No new image generated — left unchanged; stopping for today.")
            break
        try:
            engine.api("PUT", f"articles/{art['id']}.json", {"article": {"id": art["id"], "image": image}})
            done += 1
            print(f"   ✅ [{done}/{limit}] updated")
        except Exception as e:
            print(f"   ❌ update failed: {e}")
        time.sleep(1.0)
    print(f"\n🎉 Updated {done} post(s); {max(len(pending) - done, 0)} left for the coming days.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=15, help="Posts to update this run")
    parser.add_argument("--status", action="store_true", help="Only count posts still needing an image")
    args = parser.parse_args()
    if args.status:
        engine.require_token()
        pending = pending_articles()
        print(f"{len(pending)} post(s) still use a product photo.")
        for a in pending[:10]:
            print("  ", a.get("published_at"), a["handle"])
        return
    backfill(args.limit)


if __name__ == "__main__":
    main()
