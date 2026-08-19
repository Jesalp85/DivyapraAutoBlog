import urllib.request
import json
import ssl
import datetime
import argparse
import os

token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")")
shop_url = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com")
blog_id = int(os.environ.get("SHOPIFY_BLOG_ID", "97942077654"))
ctx = ssl.create_default_context()

def get_all_articles():
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            return data.get("articles", [])
    except Exception as e:
        print("❌ Error fetching articles from Shopify API:", e)
        return []

def check_status():
    articles = get_all_articles()
    published = [a for a in articles if a.get("published_at")]
    drafts = [a for a in articles if not a.get("published_at")]
    
    # Get current IST date
    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    today_str = now_ist.strftime("%Y-%m-%d")
    
    today_published = [a for a in published if a.get("published_at", "").startswith(today_str)]
    
    print("\n========================================================")
    print("📊 DIVYAPRABHA FOODS — DAILY BLOG SYSTEM STATUS")
    print("========================================================")
    print(f"Store: divyaprabhafoods.com | Date (IST): {today_str}")
    print(f"Total Articles in System: {len(articles)}")
    print(f"Currently Published & Live: {len(published)}")
    print(f"Drafts in Queue (Ready for Future): {len(drafts)}")
    print(f"Articles Published Today ({today_str}): {len(today_published)} / 3")
    print("========================================================\n")
    return len(today_published), len(drafts)

def publish_today(target_count=3):
    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    today_str = now_ist.strftime("%Y-%m-%d")
    
    articles = get_all_articles()
    published = [a for a in articles if a.get("published_at")]
    drafts = [a for a in articles if not a.get("published_at")]
    
    today_published = [a for a in published if a.get("published_at", "").startswith(today_str)]
    already_done = len(today_published)
    
    needed = target_count - already_done
    print(f"🚀 Running Daily Publisher for {today_str} (IST)...")
    print(f"Articles already published today: {already_done}. Needed: {needed}")
    
    if needed <= 0:
        print(f"✅ Target of {target_count} articles for today ({today_str}) is ALREADY COMPLETE!")
        return
        
    if not drafts:
        print("⚠️ Warning: No drafts available in queue! Please run queue generator script.")
        return

    # Sort drafts chronologically by ID
    drafts.sort(key=lambda x: x["id"])
    to_publish = drafts[:needed]

    times = ["09:00:00+05:30", "14:00:00+05:30", "19:00:00+05:30"]

    published_now = 0
    for idx, art in enumerate(to_publish):
        slot_idx = (already_done + idx) % 3
        pub_timestamp = f"{today_str}T{times[slot_idx]}"
        art_id = art["id"]
        title = art["title"]

        update_payload = {
            "article": {
                "id": art_id,
                "published": True,
                "published_at": pub_timestamp
            }
        }

        update_url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles/{art_id}.json"
        data_bytes = json.dumps(update_payload).encode("utf-8")
        update_req = urllib.request.Request(update_url, data=data_bytes, headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }, method="PUT")

        try:
            with urllib.request.urlopen(update_req, context=ctx) as u_resp:
                published_now += 1
                print(f"✅ Published Live ({today_str} {times[slot_idx][:5]}): '{title}' (ID: {art_id})")
        except Exception as e:
            print(f"❌ Error publishing article {art_id}:", e)

    print(f"\n🎉 Successfully published {published_now} new articles for today ({today_str})!")
    check_status()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Divyaprabha Daily Blog Publisher")
    parser.add_argument("--status", action="store_true", help="Check current status")
    parser.add_argument("--now", action="store_true", help="Publish today's missing daily articles")
    args = parser.parse_args()

    if args.status:
        check_status()
    else:
        publish_today()
