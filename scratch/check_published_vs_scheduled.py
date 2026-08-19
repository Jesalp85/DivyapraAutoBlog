import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

def check_all():
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles = data.get("articles", [])

    print(f"TOTAL ARTICLES IN BLOG: {len(articles)}")
    
    visible_count = 0
    hidden_count = 0
    
    today_str = "2026-08-11"
    
    published_today = []
    published_future = []
    
    for a in articles:
        pub_at = a.get("published_at")
        # In Shopify, if an article is visible on store, published_at is set. If hidden/draft, published_at is None.
        # Wait, if published_at is set to future date in REST API, is it visible or hidden?
        # Let's check a.get("published") if present or published_at
        title = a["title"]
        aid = a["id"]
        
        # Let's inspect the fields returned by Shopify API for a sample
        if pub_at and pub_at.startswith(today_str):
            published_today.append(a)
        elif pub_at and pub_at > f"{today_str}T23:59:59":
            published_future.append(a)
            
    print(f"\nArticles with published_at = TODAY ({today_str}): {len(published_today)}")
    print(f"Articles with published_at > TODAY (FUTURE): {len(published_future)}")
    
    # Print sample of future articles and their exact keys
    if articles:
        sample = articles[0]
        print("\nSample Article API Keys:", list(sample.keys()))
        print("Sample published_at:", sample.get("published_at"))
        
if __name__ == "__main__":
    check_all()
