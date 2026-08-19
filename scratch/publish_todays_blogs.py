import os
import urllib.request
import json
import ssl
import re

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

# Read DIVYAPRABHA_BLOG_POSTS.md
with open("DIVYAPRABHA_BLOG_POSTS.md", "r", encoding="utf-8") as f:
    content = f.read()

# Today's articles are 16 to 20
articles_data = [
    {
        "num": 16,
        "title": "Gunda Keri Pickle Online: Gujarati Lasode Ka Achar Guide",
        "tags": "Heritage Recipes",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "excerpt": "Discover why Kathiyawadi Gunda Keri pickle (wild glueberry stuffed with raw mango, yellow mustard kuria, and wood-pressed mustard oil) is Saurashtra's most prized seasonal achaar delicacy."
    },
    {
        "num": 17,
        "title": "Gujarati Chhundo Pickle Online: Authentic Sun-Cured Mango",
        "tags": "Artisanal Craft",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "excerpt": "Taste the golden sweetness of authentic sun-infused Gujarati Chhundo pickle made with grated Rajapuri mangoes, organic jaggery, and zero refined sugar or artificial syrup."
    },
    {
        "num": 18,
        "title": "Chana Keri Methi Achar: Sprouted Chickpea Mango Pickle",
        "tags": "Health & Spices",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "excerpt": "Discover the protein-rich health benefits and nutty taste of traditional Gujarati Chana Keri Methi achaar combining soaked Bengal gram, fenugreek seeds, and raw mango in mustard oil."
    },
    {
        "num": 19,
        "title": "Katka Keri Pickle Gujarati: Traditional Cut Mango Achar",
        "tags": "Buying Guides",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "excerpt": "Experience the satisfying crunch of traditional Katka Keri pickle made from bite-sized Rajapuri mango cubes infused with split yellow mustard, hing, and cold-pressed mustard oil."
    },
    {
        "num": 20,
        "title": "Jaggery Gor Keri Achar: Traditional Sweet Mango Pickle",
        "tags": "Pickle Pairings",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "excerpt": "Discover why pure organic jaggery elevates traditional Gujarati Gor Keri pickle into an iron-rich, sweet and tangy culinary masterpiece with zero refined sugar."
    }
]

# Extract HTML content for each article from markdown
results = []
for art in articles_data:
    pattern = rf"## 🌟 TODAY'S BATCH \(AUGUST 10, 2026\) — ARTICLE {art['num']}:.*?\`\`\`html\n(.*?)\n\`\`\`"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        html_body = match.group(1).strip()
        art["html_body"] = html_body
        results.append(art)
    else:
        print(f"ERROR: Could not find HTML body for article {art['num']}")

print(f"Extracted {len(results)} articles. Publishing now...")

published_count = 0
for art in results:
    payload = {
        "article": {
            "title": art["title"],
            "author": art["author"],
            "tags": art["tags"],
            "summary_html": art["excerpt"],
            "body_html": art["html_body"],
            "published": True
        }
    }
    
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            resp_data = json.loads(resp.read().decode())
            created_art = resp_data.get("article", {})
            published_count += 1
            print(f"✅ [{published_count}/5] Published: '{created_art.get('title')}' (ID: {created_art.get('id')}, Handle: {created_art.get('handle')})")
    except Exception as e:
        print(f"❌ Error publishing '{art['title']}':", e)

print(f"\n🎉 DONE! {published_count} out of 5 articles successfully published live to Shopify!")
