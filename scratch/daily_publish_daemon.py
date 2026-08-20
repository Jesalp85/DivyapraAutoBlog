import urllib.request
import json
import ssl
import datetime
import argparse
import os

token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
shop_url = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com")
blog_id = int(os.environ.get("SHOPIFY_BLOG_ID", "97942077654"))
ctx = ssl.create_default_context()

def get_all_articles():
    if not token:
        print("❌ Error: SHOPIFY_ACCESS_TOKEN environment variable is not set!")
        return []
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
    
    # Get current IST date & time
    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    today_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%H:%M:%S")
    
    today_published = [a for a in published if a.get("published_at", "").startswith(today_str)]
    
    print("\n========================================================")
    print("📊 DIVYAPRABHA FOODS — DAILY BLOG SYSTEM STATUS")
    print("========================================================")
    print(f"Store: divyaprabhafoods.com | Date (IST): {today_str} {time_str}")
    print(f"Total Articles in System: {len(articles)}")
    print(f"Currently Published & Live: {len(published)}")
    print(f"Drafts in Queue (Ready for Future): {len(drafts)}")
    print(f"Articles Published Today ({today_str}): {len(today_published)} / 3")
    print("========================================================\n")
    return len(today_published), len(drafts)

def get_target_for_current_time(now_ist):
    """
    Determine how many articles should be published by this time today:
    - Before 14:00 (2 PM) IST: Target = 1 (Slot 1: 09:00 AM)
    - Between 14:00 and 19:00 (7 PM) IST: Target = 2 (Slot 2: 02:00 PM)
    - 19:00 IST or later: Target = 3 (Slot 3: 07:00 PM)
    """
    hour = now_ist.hour
    if hour < 14:
        return 1
    elif hour < 19:
        return 2
    else:
        return 3

def publish_today(override_target=None):
    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    today_str = now_ist.strftime("%Y-%m-%d")
    
    if override_target is not None:
        target_count = override_target
    else:
        target_count = get_target_for_current_time(now_ist)

    articles = get_all_articles()
    if not articles and not token:
        return

    published = [a for a in articles if a.get("published_at")]
    drafts = [a for a in articles if not a.get("published_at")]
    
    today_published = [a for a in published if a.get("published_at", "").startswith(today_str)]
    already_done = len(today_published)
    
    needed = target_count - already_done
    print(f"🚀 Running Daily Publisher for {today_str} at {now_ist.strftime('%H:%M:%S')} IST...")
    print(f"Time Window Target: {target_count} post(s) expected by this time.")
    print(f"Articles already published today: {already_done}. Needed for this window: {max(0, needed)}")
    
    if needed <= 0:
        print(f"✅ Target of {target_count} article(s) for current time slot ({today_str}) is ALREADY COMPLETE!")
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
        slot_idx = already_done + idx
        if slot_idx >= 3:
            slot_idx = 2
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

    print(f"\n🎉 Successfully published {published_now} new article(s) for current slot!")
    check_status()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Divyaprabha Daily Blog Publisher")
    parser.add_argument("--status", action="store_true", help="Check current status")
    parser.add_argument("--now", action="store_true", help="Publish today's missing daily articles for current slot")
    parser.add_argument("--all", action="store_true", help="Force publish all 3 articles for today regardless of time")
    args = parser.parse_args()

    if args.status:
        check_status()
    elif args.all:
        publish_today(override_target=3)
    else:
        publish_today()

