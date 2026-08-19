import os
import urllib.request
import json
import ssl
import re

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654

ctx = ssl.create_default_context()

ALLOWED_TAGS = {"Heritage Recipes", "Health & Spices", "Buying Guides", "Pickle Pairings", "Artisanal Craft"}
VALID_HANDLES = {
    "mango-pickle-traditional-keri-achar-gujarati",
    "gor-keri-pickle-jaggery-mango-achar-gujarati",
    "chhundo-pickle-sweet-shredded-mango-achar-gujarati",
    "chana-keri-methi-pickle-gujarati-methia-achar",
    "gunda-keri-pickle-lasode-ka-achar-gujarati",
    "katka-keri-pickle-homemade-gujarati-mango-achar",
    "sweet-mango-pickle-meethi-keri-achar-homemade"
}
VALID_CDN_IMAGES = [
    "SpecialMangoBig.webp",
    "Gor_Keri_500g.webp",
    "ChhundoBigFront.webp",
    "Chana_Keri_Methi_Big.webp",
    "GundaKeriBig.webp",
    "KatkaKeriBigfront_jpg.webp",
    "SweetmangoBigFront.webp"
]

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split())

def fetch_all_articles():
    articles = []
    page_info = None
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles.extend(data.get("articles", []))
        
    return articles

def audit():
    articles = fetch_all_articles()
    print(f"Total Articles Found: {len(articles)}")
    
    audit_results = []
    
    for a in articles:
        aid = a["id"]
        title = a["title"]
        title_len = len(title)
        tags_raw = a.get("tags", "")
        tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
        body = a.get("body_html", "")
        published_at = a.get("published_at")
        
        # 1. Word count
        text = clean_html(body)
        word_count = len(text.split())
        
        # 2. Title length check (strictly under 60 chars)
        title_ok = title_len <= 60
        
        # 3. Tag taxonomy check
        invalid_tags = [t for t in tags_list if t not in ALLOWED_TAGS]
        tags_ok = len(invalid_tags) == 0 and len(tags_list) > 0
        
        # 4. JSON-LD Schemas check
        has_article_schema = '"@type": "Article"' in body or '"@type":"Article"' in body or 'schema.org/Article' in body or 'Article' in body and '<script type="application/ld+json">' in body
        has_faq_schema = '"@type": "FAQPage"' in body or '"@type":"FAQPage"' in body or 'FAQPage' in body
        
        # 5. Product links check
        product_links = re.findall(r'href=["\'](/products/[^"\'\?#]+)', body)
        invalid_product_links = [p for p in product_links if p.replace("/products/", "") not in VALID_HANDLES]
        
        # 6. FAQ section in body
        has_faq_section = "FAQ" in body or "Frequently Asked Questions" in body or "faqs" in body.lower()
        
        # 7. Authentic CDN Jar Image / CTA check
        has_cdn_image = any(img in body for img in VALID_CDN_IMAGES) or (a.get("image") and any(img in a["image"].get("src", "") for img in VALID_CDN_IMAGES))
        has_cta_card = "dp-product-card" in body or "Buy Authentic" in body or "Buy " in body or "buy-button" in body
        
        # 8. Alt tag check
        alts = re.findall(r'<img [^>]*alt=["\']([^"\'\.]+)["\']', body)
        missing_alt = len(re.findall(r'<img [^>]*src=', body)) > len(re.findall(r'<img [^>]*alt=', body))
        
        item_audit = {
            "id": aid,
            "title": title,
            "title_len": title_len,
            "published_at": published_at,
            "word_count": word_count,
            "title_ok": title_ok,
            "tags": tags_list,
            "invalid_tags": invalid_tags,
            "has_article_schema": has_article_schema,
            "has_faq_schema": has_faq_schema,
            "has_faq_section": has_faq_section,
            "invalid_product_links": invalid_product_links,
            "has_cdn_image": has_cdn_image,
            "has_cta_card": has_cta_card,
            "missing_alt": missing_alt
        }
        audit_results.append(item_audit)
        
    with open("scratch/audit_report.json", "w") as f:
        json.dump(audit_results, f, indent=2)
        
    print("Audit Complete! Report saved to scratch/audit_report.json")

if __name__ == "__main__":
    audit()
