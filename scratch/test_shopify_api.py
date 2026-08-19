import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"

# Test 1: Get Blogs
url = f"{shop_url}/admin/api/2024-04/blogs.json"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

ctx = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        print("SUCCESS! Blogs response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print("REST Error:", e)
    # Test 2: Try Authorization Bearer
    req_bearer = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req_bearer, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            print("SUCCESS with Bearer! Blogs response:")
            print(json.dumps(data, indent=2))
    except Exception as e2:
        print("Bearer Error:", e2)
