import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654

ctx = ssl.create_default_context()
url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=25"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles = data.get("articles", [])
        print(f"Sample of latest 10 articles:")
        for a in articles[:10]:
            print(f"ID: {a['id']} | Title: {a['title'][:40]} | Published At: {a.get('published_at')}")
except Exception as e:
    print("Error:", e)
