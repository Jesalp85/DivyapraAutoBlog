import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
ctx = ssl.create_default_context()

url = f"{shop_url}/admin/api/2024-04/menus.json"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        menus = data.get("menus", [])
        print(f"Total Menus: {len(menus)}")
        for m in menus:
            print(f"ID: {m['id']} | Title: '{m['title']}' | Handle: '{m['handle']}'")
            for item in m.get("items", []):
                print(f"   - {item.get('title')} -> {item.get('url')}")
except Exception as e:
    print("Error:", e)
