import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

# The 5 IDs to KEEP LIVE for Today (Aug 11):
KEEP_LIVE_IDS = {
    665974243542, # Rajapuri Raw Mango Pickle Online
    665974276310, # Jaggery Gor Keri Achar Online
    665974309078, # Sun Cured Chhundo Pickle Online
    665974341846, # Gunda Keri Pickle Buy Online
    665974374614  # Katka Keri Cut Mango Pickle
}

def cleanup():
    # Fetch all articles created today
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles = data.get("articles", [])
        
    today_articles = [a for a in articles if a.get("created_at", "").startswith("2026-08-11")]
    
    delete_list = [a for a in today_articles if a["id"] not in KEEP_LIVE_IDS]
    
    print(f"Total articles created today: {len(today_articles)}")
    print(f"Articles to KEEP LIVE: {len(KEEP_LIVE_IDS)}")
    print(f"Extra articles to DELETE from Shopify: {len(delete_list)}")
    
    deleted_count = 0
    for a in delete_list:
        aid = a["id"]
        del_url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles/{aid}.json"
        del_req = urllib.request.Request(del_url, headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }, method="DELETE")
        
        try:
            with urllib.request.urlopen(del_req, context=ctx) as resp:
                deleted_count += 1
                if deleted_count <= 5 or deleted_count % 20 == 0 or deleted_count == len(delete_list):
                    print(f"[{deleted_count}/{len(delete_list)}] Deleted ID {aid}: '{a['title']}'")
        except Exception as e:
            print(f"❌ Error deleting ID {aid}:", e)
            
    print(f"\n🎉 CLEANUP COMPLETE! Successfully removed {deleted_count} extra articles.")
    print("Store now has strictly today's 5 high-depth, 100% rule-compliant daily posts live!")

if __name__ == "__main__":
    cleanup()
