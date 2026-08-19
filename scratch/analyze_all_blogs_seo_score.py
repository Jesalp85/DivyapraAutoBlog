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

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split())

def fetch_all_articles():
    articles = []
    url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json?limit=250"
    
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    })
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        articles.extend(data.get("articles", []))
        
    return articles

def analyze_article(art):
    aid = art["id"]
    title = art.get("title", "")
    body_html = art.get("body_html", "")
    tags_list = [t.strip() for t in art.get("tags", "").split(",") if t.strip()]
    published_at = art.get("published_at", "")
    handle = art.get("handle", "")
    
    clean_text = clean_html(body_html)
    words = clean_text.split()
    word_count = len(words)
    
    # 1. Title Length & Focus Keyword (15 Pts)
    title_len = len(title)
    title_score = 0
    if title_len <= 60:
        title_score += 10
    elif title_len <= 65:
        title_score += 6
    else:
        title_score += 3
        
    # Check if title has focus keyword upfront
    if any(k in title.lower() for k in ["pickle", "achar", "keri", "chhundo", "gunda", "mango"]):
        title_score += 5
        
    # 2. Word Count & Content Depth (15 Pts)
    word_score = 0
    if word_count >= 1200:
        word_score = 15
    elif word_count >= 900:
        word_score = 12
    elif word_count >= 600:
        word_score = 8
    else:
        word_score = 4
        
    # 3. Structured Data JSON-LD Schemas (15 Pts)
    schema_score = 0
    has_article_schema = bool(re.search(r'"@type"\s*:\s*"Article"', body_html) or re.search(r'"@type"\s*:\s*"BlogPosting"', body_html))
    has_faq_schema = bool(re.search(r'"@type"\s*:\s*"FAQPage"', body_html))
    
    if has_article_schema:
        schema_score += 7.5
    if has_faq_schema:
        schema_score += 7.5
        
    # 4. FAQ Section (10 Pts)
    faq_score = 0
    has_faq_sec = bool("faq" in body_html.lower() or "frequently asked" in body_html.lower() or "q1:" in body_html.lower())
    if has_faq_sec:
        faq_score = 10
        
    # 5. Product CTA Card & Real Store CDN Images (15 Pts)
    cta_score = 0
    has_cta = bool("dp-cta-box" in body_html or "cta" in body_html.lower() or "buy" in body_html.lower())
    has_cdn_img = bool("cdn.shopify.com" in body_html or "divyaprabhafoods.com/cdn" in body_html)
    
    if has_cta:
        cta_score += 7.5
    if has_cdn_img:
        cta_score += 7.5
        
    # 6. Product Link Safety (10 Pts)
    link_score = 10
    product_links = re.findall(r'href=["\'](/products/[^"\']+)["\']', body_html)
    invalid_links = []
    for link in product_links:
        h = link.replace("/products/", "").split("?")[0].split("#")[0]
        if h not in VALID_HANDLES:
            invalid_links.append(h)
            link_score = 0
            
    # 7. Category Tag Taxonomy (10 Pts)
    tag_score = 10
    invalid_tags = [t for t in tags_list if t not in ALLOWED_TAGS]
    if invalid_tags:
        tag_score = 5 if len(invalid_tags) == 1 else 0
        
    # 8. Content Uniqueness & Non-Boilerplate Structure (10 Pts)
    unique_score = 10
    if "When culinary enthusiasts and home cooks search for authentic" in body_html:
        unique_score -= 5
    if "1.What Makes Authentic" in body_html or "1. What Makes Authentic" in body_html:
        unique_score -= 5
    unique_score = max(0, unique_score)
    
    total_score = title_score + word_score + schema_score + faq_score + cta_score + link_score + tag_score + unique_score
    
    grade = "A+" if total_score >= 95 else ("A" if total_score >= 85 else ("B" if total_score >= 70 else "C"))
    
    return {
        "id": aid,
        "title": title,
        "title_len": title_len,
        "word_count": word_count,
        "tags": tags_list,
        "invalid_tags": invalid_tags,
        "published_at": published_at,
        "handle": handle,
        "scores": {
            "title": title_score,
            "word_count": word_score,
            "schema": schema_score,
            "faq": faq_score,
            "cta_img": cta_score,
            "link_safety": link_score,
            "tag_taxonomy": tag_score,
            "uniqueness": unique_score
        },
        "total_score": round(total_score, 1),
        "grade": grade,
        "has_article_schema": has_article_schema,
        "has_faq_schema": has_faq_schema,
        "has_cta": has_cta,
        "invalid_links": invalid_links
    }

def main():
    print("Fetching and analyzing all blog articles from Divyaprabha Foods...")
    articles = fetch_all_articles()
    print(f"Total Published Articles Found: {len(articles)}")
    
    results = [analyze_article(a) for a in articles]
    
    # Sort by total score descending
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    avg_score = sum(r["total_score"] for r in results) / len(results) if results else 0
    a_plus_count = sum(1 for r in results if r["grade"] == "A+")
    a_count = sum(1 for r in results if r["grade"] == "A")
    b_count = sum(1 for r in results if r["grade"] == "B")
    c_count = sum(1 for r in results if r["grade"] == "C")
    
    print("\n=======================================================")
    print(f"OVERALL BLOG PORTFOLIO SEO SCORE: {avg_score:.1f} / 100")
    print(f"Grade Breakdown: A+ ({a_plus_count}), A ({a_count}), B ({b_count}), C ({c_count})")
    print("=======================================================\n")
    
    with open("scratch/seo_audit_full_results.json", "w") as f:
        json.dump({
            "avg_score": round(avg_score, 1),
            "total_articles": len(articles),
            "grade_distribution": {"A+": a_plus_count, "A": a_count, "B": b_count, "C": c_count},
            "articles": results
        }, f, indent=2)
        
    print("Full report saved to scratch/seo_audit_full_results.json")

if __name__ == "__main__":
    main()
