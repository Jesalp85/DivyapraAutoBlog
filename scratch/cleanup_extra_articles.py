import os
import urllib.request
import json
import ssl
import time

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

cutoff_id = 665945178326  # Today's 5th valid article ID

print("Fetching all extra articles created by the batch run...")

deleted_count = 0

while True:
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            articles = data.get("articles", [])
            
            # Find articles created in batch run (ID > cutoff_id)
            extra_articles = [a for a in articles if a["id"] > cutoff_id]
            
            if not extra_articles:
                print("No more extra articles found to delete.")
                break
                
            print(f"Found {len(extra_articles)} extra articles in this page. Deleting now...")
            
            for a in extra_articles:
                del_url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles/{a['id']}.json"
                del_req = urllib.request.Request(del_url, method="DELETE", headers={
                    "X-Shopify-Access-Token": token
                })
                try:
                    with urllib.request.urlopen(del_req, context=ctx) as del_resp:
                        deleted_count += 1
                        print(f"[{deleted_count}] Deleted extra article ID {a['id']}: '{a['title'][:40]}'")
                except Exception as e:
                    print(f"Error deleting article {a['id']}:", e)
                time.sleep(0.1)
    except Exception as e:
        print("Error fetching articles:", e)
        break

print(f"\n✅ CLEANUP COMPLETE! Total deleted extra articles: {deleted_count}")
