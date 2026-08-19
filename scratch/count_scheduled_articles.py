import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654

ctx = ssl.create_default_context()
url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles/count.json"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        print(f"TOTAL ARTICLES IN BLOG: {data.get('count')}")
except Exception as e:
    print("Error:", e)
