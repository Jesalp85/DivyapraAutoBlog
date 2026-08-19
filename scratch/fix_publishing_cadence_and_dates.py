import os
import urllib.request
import json
import ssl
import datetime

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

def fix_cadence():
    # 1. Fetch all articles from Shopify
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": token})

    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles = data.get("articles", [])

    print(f"Total articles found in store: {len(articles)}")

    # Sort articles chronologically by creation ID / order
    articles.sort(key=lambda x: x["id"])

    # Define target publishing calendar: 3 articles per day starting Aug 11, 2026 up to Aug 19, 2026
    start_date = datetime.date(2026, 8, 11)
    today = datetime.date(2026, 8, 19)

    times = ["09:00:00+05:30", "14:00:00+05:30", "19:00:00+05:30"]

    published_live_count = 0
    draft_scheduled_count = 0

    curr_date = start_date

    for i, art in enumerate(articles):
        art_id = art["id"]
        title = art["title"]

        if curr_date <= today:
            # Assign exact daily date (3 articles per day)
            time_str = times[i % 3]
            target_pub_at = f"{curr_date.isoformat()}T{time_str}"

            update_payload = {
                "article": {
                    "id": art_id,
                    "published": True,
                    "published_at": target_pub_at
                }
            }
            published_live_count += 1
            print(f"✅ Live [{curr_date.isoformat()}] (#{published_live_count}): '{title[:45]}...'")

            if (i + 1) % 3 == 0:
                curr_date += datetime.timedelta(days=1)
        else:
            # Future articles: set published=False so they stay as Drafts in Shopify Admin
            update_payload = {
                "article": {
                    "id": art_id,
                    "published": False
                }
            }
            draft_scheduled_count += 1
            print(f"📦 Draft/Scheduled for Future (#{draft_scheduled_count}): '{title[:45]}...'")

        # Execute API Update
        update_url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles/{art_id}.json"
        data_bytes = json.dumps(update_payload).encode("utf-8")
        update_req = urllib.request.Request(update_url, data=data_bytes, headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }, method="PUT")

        try:
            with urllib.request.urlopen(update_req, context=ctx) as u_resp:
                pass
        except Exception as e:
            print(f"❌ Error updating article {art_id}:", e)

    print("\n========================================================")
    print("🎉 PUBLISHING CADENCE & DATES FIXED COMPLIANT WITH RULES!")
    print(f"✅ Published & Dated Live (Aug 11 - Aug 19): {published_live_count} Articles (3/day)")
    print(f"📦 Scheduled Drafts in Shopify (Ready for Future Days): {draft_scheduled_count} Articles")
    print("========================================================")

if __name__ == "__main__":
    fix_cadence()
