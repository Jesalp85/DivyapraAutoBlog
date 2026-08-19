import os
import urllib.request
import json
import ssl
import datetime

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654
ctx = ssl.create_default_context()

PRODUCTS = [
    {
        "name": "Homemade Mango Pickle (Aam Ka Achar)",
        "handle": "mango-pickle-traditional-keri-achar-gujarati",
        "link": "/products/mango-pickle-traditional-keri-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SpecialMangoBig.webp?v=1782721972",
        "desc": "Handcrafted Rajapuri Raw Mango Achar with Cold-Pressed Yellow Mustard Oil & Traditional Spices."
    },
    {
        "name": "Gor Keri Jaggery Mango Pickle",
        "handle": "gor-keri-pickle-jaggery-mango-achar-gujarati",
        "link": "/products/gor-keri-pickle-jaggery-mango-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Gor_Keri_500g.webp?v=1784831601",
        "desc": "100% Refined Sugar-Free Sweet Mango Pickle with Organic Jaggery, Cinnamon & Kashmiri Red Chilli."
    },
    {
        "name": "Chhundo Sweet Shredded Mango Pickle",
        "handle": "chhundo-pickle-sweet-shredded-mango-achar-gujarati",
        "link": "/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/ChhundoBigFront.webp?v=1782723201",
        "desc": "Traditional Sun-Cured Shredded Rajapuri Raw Mango Relish with Roasted Cumin & Organic Jaggery."
    },
    {
        "name": "Gunda Keri Glueberry Pickle",
        "handle": "gunda-keri-pickle-lasode-ka-achar-gujarati",
        "link": "/products/gunda-keri-pickle-lasode-ka-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/GundaKeriBig.webp?v=1782723036",
        "desc": "Seasonal Wild Lasode Glueberries Stuffed with Shredded Raw Mango & Yellow Mustard Kuria."
    },
    {
        "name": "Katka Keri Cut Mango Pickle",
        "handle": "katka-keri-pickle-homemade-gujarati-mango-achar",
        "link": "/products/katka-keri-pickle-homemade-gujarati-mango-achar",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/KatkaKeriBigfront_jpg.webp?v=1784704467",
        "desc": "Crunchy Bite-Sized Rajapuri Cut Mango Cubes Cured in Pure Kachi Ghani Mustard Oil & Asafoetida."
    },
    {
        "name": "Meethi Keri Sweet Mango Pickle",
        "handle": "sweet-mango-pickle-meethi-keri-achar-homemade",
        "link": "/products/sweet-mango-pickle-meethi-keri-achar-homemade",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SweetmangoBigFront.webp?v=1782722922",
        "desc": "Mildly Spiced Sweet Raw Mango Slices Slow-Matured in Solar Heat with Natural Jaggery Syrup."
    },
    {
        "name": "Chana Keri Methi Pickle",
        "handle": "chana-keri-methi-pickle-gujarati-methia-achar",
        "link": "/products/chana-keri-methi-pickle-gujarati-methia-achar",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Chana_Keri_Methi_Big.webp?v=1782722238",
        "desc": "Protein-Packed Gujarati Methia Achar with Soaked Chickpeas, Fenugreek Seeds & Raw Mango."
    }
]

CATEGORIES = ["Heritage Recipes", "Health & Spices", "Buying Guides", "Pickle Pairings", "Artisanal Craft"]

# Extended topics for Days 11 to 30 (100 additional scheduled posts)
EXTENDED_TOPICS = []
base_titles = [
    ("Traditional Gujarati Mango Achar Online", "Gujarati Mango Achar Online", 0, 0),
    ("Buy Organic Jaggery Gor Keri Achar Online", "Buy Organic Jaggery Gor Keri Achar", 1, 1),
    ("Authentic Sun Dried Chhundo Relish Online", "Sun Dried Chhundo Relish Online", 2, 4),
    ("Wild Lasode Gunda Keri Pickle Buying Guide", "Gunda Keri Pickle Buying Guide", 3, 2),
    ("Crispy Skin On Katka Keri Mango Achar", "Skin On Katka Keri Mango Achar", 4, 0),
    ("Homemade Meethi Keri Sweet Mango Achar", "Homemade Meethi Keri Sweet Mango Achar", 5, 4),
    ("Nutty Fenugreek Chana Keri Methia Achar", "Fenugreek Chana Keri Methia Achar", 6, 1),
    ("Wood Pressed Kachi Ghani Mustard Oil Achar", "Wood Pressed Kachi Ghani Mustard Oil Achar", 0, 1),
    ("Why Indian Pickles Support Digestive Health", "Indian Pickles Digestive Health", 0, 1),
    ("Traditional Gujarati Breakfast Pickle Pairings", "Gujarati Breakfast Pickle Pairings", 1, 3)
]

for d in range(100):
    bt, kw, pi, ci = base_titles[d % len(base_titles)]
    title = f"{bt} Vol {d+1}"
    EXTENDED_TOPICS.append((title, kw, pi, ci))

def generate_article_html(title, keyword, prod_idx):
    p = PRODUCTS[prod_idx]
    return f"""
<!-- JSON-LD Article Schema -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "author": {{
    "@type": "Organization",
    "name": "Baa & The DivyaPrabha Culinary Team"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Divyaprabha Foods",
    "logo": {{
      "@type": "ImageObject",
      "url": "https://divyaprabhafoods.com/cdn/shop/files/logo.png"
    }}
  }},
  "datePublished": "2026-08-21",
  "description": "Discover authentic {title}. Handcrafted with 100% natural ingredients, wood-pressed yellow mustard oil, and traditional Saurashtra recipes."
}}
</script>

<!-- JSON-LD FAQPage Schema -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "What makes DivyaPrabha {p['name']} authentic?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "DivyaPrabha {p['name']} is handcrafted using Baa's 45+ year old Saurashtra family recipe with 100% natural ingredients, wood-pressed yellow mustard oil, sun-drying rituals, and zero artificial preservatives."
      }}
    }},
    {{
      "@type": "Question",
      "name": "How is {keyword} prepared naturally?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Natural solar sun-drying removes moisture, while anti-microbial Sendha Namak, turmeric, split mustard seeds (Rai Kuria), and complete submersion in cold-pressed mustard oil preserve the pickle naturally for over 12 months."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Where can I buy authentic {keyword} online?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "You can order authentic handcrafted {p['name']} direct from Saurashtra online at DivyaPrabha Foods (divyaprabhafoods.com)."
      }}
    }}
  ]
}}
</script>

<p class="dp-lead">
  Looking for authentic <strong>{keyword}</strong>? At DivyaPrabha Foods, every jar of <strong>{p['name']}</strong> is handcrafted in small batches following Baa's 45-year-old Saurashtra family heritage.
</p>

<h2>The Heritage & Quality of {keyword}</h2>
<p>
  Unlike industrial store-bought pickles filled with cheap palm oil, sodium benzoate, and synthetic acetic acid, authentic <strong>{keyword}</strong> relies on patience, solar heat, and premium raw ingredients.
</p>

<!-- Visual Product CTA Card -->
<div class="dp-product-card" style="background: #fdf6ed; border: 1px solid #e8d5c0; border-radius: 16px; padding: 24px; margin: 32px 0; text-align: center; box-shadow: 0 4px 12px rgba(61,31,15,0.05);">
  <img src="{p['image']}" alt="{p['name']} Jar - Divyaprabha Foods" style="max-width: 240px; width: 100%; height: auto; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
  <h3 style="color: #b01215; margin: 8px 0 12px 0; font-size: 20px;">Authentic {p['name']}</h3>
  <p style="color: #3d1f0f; font-size: 14px; margin-bottom: 16px;">{p['desc']}</p>
  <a href="{p['link']}" style="background: #b01215; color: #ffffff; padding: 12px 32px; border-radius: 50px; font-weight: bold; text-decoration: none; display: inline-block;">Buy Authentic {p['name']} Online →</a>
</div>

<h2>Key Ingredients & Health Benefits</h2>
<ul>
  <li><strong>Wood-Pressed Yellow Mustard Oil:</strong> Rich in natural Omega-3 fatty acids, providing anti-microbial preservation and gut warmth.</li>
  <li><strong>Rai Kuria & Methi Kuria:</strong> Coarsely split yellow mustard and fenugreek seeds for digestive support.</li>
  <li><strong>Sendha Namak:</strong> Mineral rock salt that enhances natural tanginess.</li>
  <li><strong>Zero Artificial Chemicals:</strong> Free from artificial colors, synthetic vinegar, or palm oil.</li>
</ul>

<h2>Frequently Asked Questions (FAQs)</h2>
<h3>1. What makes DivyaPrabha {p['name']} authentic?</h3>
<p>It is handcrafted in small batches using Baa's 45+ year heritage Saurashtra recipe with 100% natural ingredients and wood-pressed mustard oil.</p>

<h3>2. How is {keyword} preserved without chemical preservatives?</h3>
<p>Solar sun-drying, mineral rock salt, turmeric, and full submersion in pure cold-pressed mustard oil preserve the pickle naturally for over 12 months.</p>

<h3>3. Where can I buy authentic {keyword} online?</h3>
<p>You can buy authentic handcrafted {p['name']} online directly from Saurashtra at DivyaPrabha Foods (divyaprabhafoods.com).</p>

<p style="text-align: center; margin-top: 30px;">
  <a href="{p['link']}" style="background: #b01215; color: #ffffff; padding: 14px 32px; border-radius: 50px; font-weight: bold; text-decoration: none; display: inline-block;">Order Handcrafted {p['name']} Online Direct from Saurashtra →</a>
</p>
"""

# Schedule Days 11 to 30 (August 21 to September 9, 2026)
start_date = datetime.date(2026, 8, 21)
posting_times = ["09:00:00+05:30", "12:00:00+05:30", "15:00:00+05:30", "18:00:00+05:30", "21:00:00+05:30"]

success_count = 0
for idx in range(len(EXTENDED_TOPICS)):
    title, keyword, prod_idx, cat_idx = EXTENDED_TOPICS[idx]
    category = CATEGORIES[cat_idx]
    
    day_offset = idx // 5
    time_idx = idx % 5
    sched_date = start_date + datetime.timedelta(days=day_offset)
    sched_timestamp = f"{sched_date.isoformat()}T{posting_times[time_idx]}"
    
    html_body = generate_article_html(title, keyword, prod_idx)
    excerpt = f"Discover authentic {title}. Handcrafted with 100% natural ingredients, wood-pressed yellow mustard oil, and Baa's heritage Saurashtra recipe."
    
    payload = {
        "article": {
            "title": title[:59],
            "author": "Baa & The DivyaPrabha Culinary Team",
            "tags": category,
            "summary_html": excerpt,
            "body_html": html_body,
            "published": False,
            "published_at": sched_timestamp
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
            art = resp_data.get("article", {})
            success_count += 1
            print(f"[{success_count}/100] Scheduled for {sched_timestamp} -> Title: '{art.get('title')}' (ID: {art.get('id')})")
    except Exception as e:
        print(f"❌ Error scheduling '{title}':", e)

print(f"\n==========================================")
print(f"🎉 DAYS 11-30 AUTOMATED SCHEDULING COMPLETE!")
print(f"Successfully Scheduled Days 11-30: {success_count} Articles")
print(f"==========================================")
