import json

with open("scratch/audit_report.json") as f:
    data = json.load(f)

print(f"Total Published Articles Audited: {len(data)}\n")

rule_stats = {
    "word_count_1200": 0,
    "title_len_under_60": 0,
    "valid_tags_only": 0,
    "article_schema": 0,
    "faq_schema": 0,
    "faq_section": 0,
    "valid_product_links": 0,
    "cdn_product_image": 0,
    "cta_card": 0
}

failures = []

for idx, a in enumerate(data, 1):
    wc_ok = a["word_count"] >= 1200
    tlen_ok = a["title_ok"]
    tags_ok = len(a["invalid_tags"]) == 0 and len(a["tags"]) > 0
    art_sch_ok = a["has_article_schema"]
    faq_sch_ok = a["has_faq_schema"]
    faq_sec_ok = a["has_faq_section"]
    plink_ok = len(a["invalid_product_links"]) == 0
    cdn_ok = a["has_cdn_image"]
    cta_ok = a["has_cta_card"]
    
    if wc_ok: rule_stats["word_count_1200"] += 1
    if tlen_ok: rule_stats["title_len_under_60"] += 1
    if tags_ok: rule_stats["valid_tags_only"] += 1
    if art_sch_ok: rule_stats["article_schema"] += 1
    if faq_sch_ok: rule_stats["faq_schema"] += 1
    if faq_sec_ok: rule_stats["faq_section"] += 1
    if plink_ok: rule_stats["valid_product_links"] += 1
    if cdn_ok: rule_stats["cdn_product_image"] += 1
    if cta_ok: rule_stats["cta_card"] += 1

    issues = []
    if not wc_ok: issues.append(f"Low Word Count ({a['word_count']} words, target 1200-1500+)")
    if not tlen_ok: issues.append(f"Title length too long ({a['title_len']} chars > 60 chars)")
    if not tags_ok: issues.append(f"Invalid/Missing Tags: {a['invalid_tags']} (Assigned: {a['tags']})")
    if not art_sch_ok: issues.append("Missing JSON-LD Article Schema")
    if not faq_sch_ok: issues.append("Missing JSON-LD FAQPage Schema")
    if not faq_sec_ok: issues.append("Missing FAQ Section in Body")
    if not plink_ok: issues.append(f"Invalid Product Links: {a['invalid_product_links']}")
    if not cdn_ok: issues.append("Missing authentic CDN product image")
    if not cta_ok: issues.append("Missing 1-to-1 Product CTA Card")

    print(f"{idx}. [{a['published_at'][:10]}] \"{a['title']}\"")
    print(f"   Words: {a['word_count']} | Title Chars: {a['title_len']} | Tags: {a['tags']}")
    if issues:
        print(f"   ❌ Issues Found ({len(issues)}):")
        for iss in issues:
            print(f"      - {iss}")
    else:
        print(f"   ✅ 100% Compliant with all Rules!")
    print("-" * 70)

print("\n=== RULE COMPLIANCE SUMMARY ===")
total = len(data)
for k, v in rule_stats.items():
    pct = (v / total) * 100
    print(f"{k:25s}: {v}/{total} ({pct:.1f}%)")
