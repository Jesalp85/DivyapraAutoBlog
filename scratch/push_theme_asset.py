import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
ctx = ssl.create_default_context()

# 1. Fetch Themes
url = f"{shop_url}/admin/api/2024-04/themes.json"
req = urllib.request.Request(url, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        themes = data.get("themes", [])
        main_theme = None
        for t in themes:
            print(f"Theme ID: {t['id']} | Name: '{t['name']}' | Role: '{t['role']}'")
            if t.get("role") == "main":
                main_theme = t
                
        if main_theme:
            theme_id = main_theme["id"]
            print(f"\nTarget Live Main Theme: '{main_theme['name']}' (ID: {theme_id})")
            
            # Read local updated sections/dp-blog.liquid
            with open("sections/dp-blog.liquid", "r", encoding="utf-8") as f:
                dp_blog_content = f.read()
                
            # 2. Push asset to live theme
            asset_url = f"{shop_url}/admin/api/2024-04/themes/{theme_id}/assets.json"
            asset_payload = {
                "asset": {
                    "key": "sections/dp-blog.liquid",
                    "value": dp_blog_content
                }
            }
            
            asset_req = urllib.request.Request(asset_url, data=json.dumps(asset_payload).encode("utf-8"), headers={
                "X-Shopify-Access-Token": token,
                "Content-Type": "application/json"
            }, method="PUT")
            
            with urllib.request.urlopen(asset_req, context=ctx) as asset_resp:
                asset_data = json.loads(asset_resp.read().decode())
                print(f"✅ SUCCESS! Pushed updated 'sections/dp-blog.liquid' to Live Theme '{main_theme['name']}' (Key: {asset_data.get('asset', {}).get('key')})")
        else:
            print("No main live theme found!")
except Exception as e:
    print("Error:", e)
