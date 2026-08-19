import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
ctx = ssl.create_default_context()

# 1. Fetch Products
url = f"{shop_url}/admin/api/2024-04/products.json?limit=250"
req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": token})

print("--- STORE PRODUCTS ---")
products_list = []
try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        for p in data.get("products", []):
            title = p.get("title")
            handle = p.get("handle")
            status = p.get("status")
            print(f"Product: '{title}' | Handle: '{handle}' | Status: '{status}'")
            products_list.append({"title": title, "handle": handle, "status": status})
except Exception as e:
    print("Error fetching products:", e)

# 2. Fetch Smart & Custom Collections
print("\n--- STORE COLLECTIONS ---")
colls_list = []
for coll_type in ["custom_collections", "smart_collections"]:
    url = f"{shop_url}/admin/api/2024-04/{coll_type}.json"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": token})
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            for c in data.get(coll_type, []):
                title = c.get("title")
                handle = c.get("handle")
                print(f"Collection: '{title}' | Handle: '{handle}'")
                colls_list.append({"title": title, "handle": handle})
    except Exception as e:
        print(f"Error fetching {coll_type}:", e)
