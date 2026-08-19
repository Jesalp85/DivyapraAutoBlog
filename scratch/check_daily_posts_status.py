import os
import urllib.request
import json
import ssl
import datetime

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

def check_status():
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles = data.get("articles", [])
        
    print(f"Total Articles Fetched: {len(articles)}")
    
    today_str = "2026-08-11"
    yesterday_str = "2026-08-10"
    
    today_posts = []
    yesterday_posts = []
    future_scheduled = []
    
    for a in articles:
        pub_at = a.get("published_at")
        created_at = a.get("created_at")
        title = a.get("title")
        aid = a.get("id")
        
        if pub_at and pub_at.startswith(today_str):
            today_posts.append(a)
        elif pub_at and pub_at.startswith(yesterday_str):
            yesterday_posts.append(a)
        elif pub_at and pub_at > f"{today_str}T23:59:59":
            future_scheduled.append(a)
            
    print(f"\n--- DAILY POST STATUS FOR TODAY ({today_str}) ---")
    print(f"Published Today: {len(today_posts)}")
    for a in today_posts:
        print(f"  - [{a['published_at']}] ID: {a['id']} | Title: {a['title']}")
        
    print(f"\n--- PUBLISHED YESTERDAY ({yesterday_str}) ---")
    print(f"Published Yesterday: {len(yesterday_posts)}")
    for a in yesterday_posts:
        print(f"  - [{a['published_at']}] ID: {a['id']} | Title: {a['title']}")

    print(f"\n--- FUTURE SCHEDULED POSTS ---")
    print(f"Scheduled for Future: {len(future_scheduled)}")
    for a in future_scheduled:
        print(f"  - [{a['published_at']}] ID: {a['id']} | Title: {a['title']}")
        
    print(f"\n--- LATEST 10 ARTICLES IN SYSTEM ---")
    for a in articles[:10]:
        pub_status = "VISIBLE" if a.get("published_at") else "DRAFT/HIDDEN"
        print(f"ID: {a['id']} | {pub_status} | Published: {a.get('published_at')} | Title: {a['title']}")

if __name__ == "__main__":
    check_status()
