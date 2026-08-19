import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"

# SSL Context
ctx = ssl.create_default_context()

# 1. Fetch Blogs
url = f"{shop_url}/admin/api/2024-04/blogs.json"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        print("SUCCESS! Blogs found:")
        print(json.dumps(data, indent=2))
        blogs = data.get("blogs", [])
        if blogs:
            blog_id = blogs[0]["id"]
            print(f"Target Blog ID: {blog_id} (Title: {blogs[0]['title']})")
        else:
            print("No blogs found!")
except Exception as e:
    print("Error fetching blogs:", e)
