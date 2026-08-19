import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.loads(resp.read().decode())
    articles = data.get("articles", [])

print(f"Total articles fetched: {len(articles)}")

# Find articles created today
today_articles = [a for a in articles if a.get("created_at", "").startswith("2026-08-11")]
print(f"Articles created today (Aug 11): {len(today_articles)}")

# Print titles of today's articles
for idx, a in enumerate(today_articles, 1):
    print(f"{idx}. ID: {a['id']} | Published At: {a.get('published_at')} | Title: {a['title']}")
