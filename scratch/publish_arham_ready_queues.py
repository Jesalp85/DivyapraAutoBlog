#!/usr/bin/env python3
"""Publish prebuilt Arham keyword queues to Shopify Admin API.

Requires a token with content + products scopes:
  export SHOPIFY_ACCESS_TOKEN=shpat_xxx

  python3 scratch/publish_arham_ready_queues.py --collections
  python3 scratch/publish_arham_ready_queues.py --blogs --limit 30
  python3 scratch/publish_arham_ready_queues.py --blogs --all
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_Q = ROOT / "scratch" / "arham_blog_queue_ready.json"
COL_Q = ROOT / "scratch" / "arham_collection_queue_ready.json"
STATE = ROOT / "scratch" / "arham_keyword_engine_state.json"

SHOP = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
BLOG_ID = int(os.environ.get("SHOPIFY_BLOG_ID", "97942077654"))
CTX = ssl.create_default_context()


def require_token():
    if not TOKEN:
        raise SystemExit("Set SHOPIFY_ACCESS_TOKEN first")


def api(method, path, payload=None):
    url = f"{SHOP}/admin/api/2024-04/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()[:400]}") from e


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"blog_handles": {}, "collection_handles": {}}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False))


def publish_collections():
    require_token()
    cols = json.loads(COL_Q.read_text())
    existing = {c["handle"]: c for c in (api("GET", "custom_collections.json?limit=250").get("custom_collections") or [])}
    st = load_state()
    for col in cols:
        handle = col["handle"]
        seo_title = col["title"][:59]
        seo_desc = f"Buy authentic {col['pillar']} homemade Gujarati pickles online from Divyaprabha Foods."[:160]
        if handle in existing:
            cid = existing[handle]["id"]
            api(
                "PUT",
                f"custom_collections/{cid}.json",
                {
                    "custom_collection": {
                        "id": cid,
                        "body_html": col["body_html"],
                        "metafields_global_title_tag": seo_title,
                        "metafields_global_description_tag": seo_desc,
                    }
                },
            )
            print("updated", handle)
        else:
            res = api(
                "POST",
                "custom_collections.json",
                {
                    "custom_collection": {
                        "title": col["title"],
                        "handle": handle,
                        "body_html": col["body_html"],
                        "published": True,
                        "metafields_global_title_tag": seo_title,
                        "metafields_global_description_tag": seo_desc,
                    }
                },
            )
            cid = (res.get("custom_collection") or {}).get("id")
            print("created", handle, cid)
            pdata = api("GET", f"products.json?handle={col['product_handle']}")
            products = pdata.get("products") or []
            if products and cid:
                try:
                    api("POST", "collects.json", {"collect": {"collection_id": cid, "product_id": products[0]["id"]}})
                except Exception as e:
                    print(" collect skip", e)
        st.setdefault("collection_handles", {})[handle] = col["title"]
        save_state(st)
        time.sleep(0.4)


def publish_blogs(limit=None):
    require_token()
    blogs = json.loads(BLOG_Q.read_text())
    st = load_state()
    done = set(st.get("blog_handles", {}))
    pending = [b for b in blogs if b["handle"] not in done]
    if limit is not None:
        pending = pending[:limit]
    print(f"Publishing {len(pending)} / remaining {len([b for b in blogs if b['handle'] not in done])}")
    for b in pending:
        payload = {
            "article": {
                "title": b["title"],
                "author": "Baa & The DivyaPrabha Culinary Team",
                "tags": b["tags"],
                "body_html": b["body_html"],
                "summary_html": b["excerpt"],
                "handle": b["handle"],
                "published": True,
                "published_at": b["published_at"],
                "image": {"src": b["image"], "alt": b["image_alt"]},
            }
        }
        try:
            res = api("POST", f"blogs/{BLOG_ID}/articles.json", payload)
            art = res.get("article") or {}
            st.setdefault("blog_handles", {})[b["handle"]] = {
                "id": art.get("id"),
                "published_at": b["published_at"],
                "title": b["title"],
                "keyword": b["keyword"],
            }
            save_state(st)
            print("✅", b["published_at"], b["title"])
        except Exception as e:
            print("❌", b["handle"], e)
        time.sleep(0.45)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--collections", action="store_true")
    p.add_argument("--blogs", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()
    if args.collections:
        publish_collections()
    if args.blogs:
        publish_blogs(None if args.all else args.limit)


if __name__ == "__main__":
    main()
