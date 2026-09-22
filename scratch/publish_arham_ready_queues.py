#!/usr/bin/env python3
"""Publish prebuilt Arham keyword queues to Shopify Admin API.

Requires a token with content + products scopes:
  export SHOPIFY_ACCESS_TOKEN=shpat_xxx

  python3 scratch/publish_arham_ready_queues.py --collections --collection-limit 2
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


def publish_collections(limit=2):
    """Create up to `limit` NEW collection pages (default 2/week cadence)."""
    require_token()
    cols = json.loads(COL_Q.read_text())
    try:
        existing = {
            c["handle"]: c
            for c in (api("GET", "custom_collections.json?limit=250").get("custom_collections") or [])
        }
    except Exception as e:
        print(f"⚠️ Skipping collections — token lacks products/collections scope: {e}")
        return

    st = load_state()
    pending = [c for c in cols if c["handle"] not in existing]
    batch = pending[: max(0, limit)]
    print(
        f"Collections: creating {len(batch)} this run "
        f"(pending {len(pending)} / queue {len(cols)}; limit={limit}/week)"
    )
    if not batch:
        print("No new collections left in queue.")
        return

    for col in batch:
        handle = col["handle"]
        seo_title = col["title"][:59]
        seo_desc = f"Buy authentic {col['pillar']} homemade Gujarati pickles online from Divyaprabha Foods."[:160]
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
        print("✅ created", handle, cid)
        try:
            pdata = api("GET", f"products.json?handle={col['product_handle']}")
            products = pdata.get("products") or []
            if products and cid:
                api("POST", "collects.json", {"collect": {"collection_id": cid, "product_id": products[0]["id"]}})
        except Exception as e:
            print(" collect skip", e)
        st.setdefault("collection_handles", {})[handle] = {
            "title": col["title"],
            "id": cid,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        save_state(st)
        time.sleep(0.4)
    print(f"Done. Created {len(batch)} collections; {len(pending) - len(batch)} remaining.")


def publish_blogs(limit=None):
    require_token()
    blogs = json.loads(BLOG_Q.read_text())
    st = load_state()
    done = set(st.get("blog_handles", {}))
    # Also skip handles already on Shopify if we can list them
    try:
        since_id = 0
        for _ in range(30):
            path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,handle"
            if since_id:
                path += f"&since_id={since_id}"
            arts = api("GET", path).get("articles") or []
            if not arts:
                break
            for a in arts:
                if a.get("handle"):
                    done.add(a["handle"])
                since_id = max(since_id, a.get("id") or 0)
            if len(arts) < 250:
                break
            time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Could not list existing articles (will rely on local state): {e}")

    pending = [b for b in blogs if b["handle"] not in done]
    if limit is not None:
        pending = pending[:limit]
    print(f"Publishing {len(pending)} / remaining {len([b for b in blogs if b['handle'] not in done])}")
    ok = 0
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
            ok += 1
            print("✅", b["published_at"], b["title"])
        except Exception as e:
            print("❌", b["handle"], e)
        time.sleep(0.45)
    print(f"Done. Created {ok} articles.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--collections", action="store_true")
    p.add_argument("--blogs", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--limit", type=int, default=30, help="Blog batch size")
    p.add_argument(
        "--collection-limit",
        type=int,
        default=2,
        help="Max NEW collections to create this run (weekly cadence = 2)",
    )
    args = p.parse_args()
    if args.collections:
        publish_collections(args.collection_limit)
    if args.blogs:
        publish_blogs(None if args.all else args.limit)


if __name__ == "__main__":
    main()
