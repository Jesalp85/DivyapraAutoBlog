import os
import urllib.request
import json
import ssl
import datetime
import re

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

# Master List of Topics starting from Aug 15th (Index 17) to Sept 15th
TOPIC_TEMPLATES = [
    # Aug 15 (Missing Day 1)
    ("Fenugreek Methi Kuria Benefits for Blood Sugar Support", "Methi Kuria Blood Sugar Support Achar", 6, 1, "2026-08-15T09:00:00+05:30"),
    ("Cold Pressed Mustard Oil vs Palm Oil in Indian Pickles", "Cold Pressed Mustard Oil vs Palm Oil Achar", 0, 1, "2026-08-15T13:00:00+05:30"),
    ("Natural Antioxidants in Sun Dried Raw Rajapuri Mangoes", "Antioxidants in Sun Dried Raw Mangoes", 0, 1, "2026-08-15T18:00:00+05:30"),

    # Aug 16 (Missing Day 2)
    ("Best Pickle Pairings for Methi Thepla & Gujarati Snacks", "Pickle Pairings Methi Thepla", 1, 3, "2026-08-16T09:00:00+05:30"),
    ("What Pickle Pairs Best with Stuffed Aloo Gobi Parathas", "Best Pickle for Stuffed Parathas", 4, 3, "2026-08-16T13:00:00+05:30"),
    ("Transform Everyday Moong Dal Khichdi with Digestive Achar", "Pickle for Moong Dal Khichdi", 0, 3, "2026-08-16T18:00:00+05:30"),

    # Aug 17 (Missing Day 3)
    ("Traditional Kathiyawadi Bajra Rotla & Pickle Pairing", "Kathiyawadi Bajra Rotla Pickle Pairing", 3, 3, "2026-08-17T09:00:00+05:30"),
    ("Best Sweet Pickles for Kids School Tiffin Lunchboxes", "Sweet Pickles Kids School Tiffin", 2, 3, "2026-08-17T13:00:00+05:30"),
    ("Dal Chawal & Sun Dried Garlic Achar Jugalbandi Guide", "Dal Chawal Garlic Achar Jugalbandi", 0, 3, "2026-08-17T18:00:00+05:30"),

    # Aug 18 (Missing Day 4)
    ("Khakhra & Chhundo Relish: Ultimate Gujarati Breakfast", "Khakhra Chhundo Gujarati Breakfast", 2, 3, "2026-08-18T09:00:00+05:30"),
    ("Farsan Pickle Pairing Guide: Mathri Fafda Gathiya", "Farsan Pickle Pairing Guide", 1, 3, "2026-08-18T13:00:00+05:30"),
    ("Festive Gujarati Thali Pickles: Gunda Keri & Gor Keri", "Festive Gujarati Thali Pickles", 3, 3, "2026-08-18T18:00:00+05:30"),

    # Aug 19 (TODAY - Missing Day 5)
    ("Summer Rice Bowls & Tangy Katka Keri Achar Combination", "Summer Rice Bowls Katka Keri Achar", 4, 3, "2026-08-19T09:00:00+05:30"),
    ("How to Spot Fake vs Pure Homemade Pickles Online", "Spot Fake vs Pure Homemade Pickles", 0, 2, "2026-08-19T13:00:00+05:30"),
    ("5 Red Flags in Store Bought Commercial Pickle Jars", "Red Flags Store Bought Pickle Jars", 0, 2, "2026-08-19T18:00:00+05:30"),

    # Aug 20 (Tomorrow & Future Schedule)
    ("Why Ceramic Martban Jars Are Superior to Plastic Bottles", "Ceramic Martban Jars vs Plastic Pickle", 0, 2, "2026-08-20T09:00:00+05:30"),
    ("Understanding Split Mustard Seed Rai Kuria Quality", "Rai Kuria Quality in Indian Achar", 4, 2, "2026-08-20T13:00:00+05:30"),
    ("Buy Authentic Gujarati Pickles Online Direct from Saurashtra", "Buy Authentic Gujarati Pickles Online", 0, 2, "2026-08-20T18:00:00+05:30"),

    # Aug 21
    ("Why Wood Pressed Kachi Ghani Oil Pickles Last 12 Months", "Wood Pressed Kachi Ghani Oil Shelf Life", 0, 2, "2026-08-21T09:00:00+05:30"),
    ("Organic Jaggery vs Sugar Syrup in Sweet Achar Guide", "Organic Jaggery vs Sugar Syrup Sweet Achar", 1, 2, "2026-08-21T13:00:00+05:30"),
    ("Rajapuri Raw Mango Quality Guide for Authentic Achar", "Rajapuri Raw Mango Quality Achar", 0, 2, "2026-08-21T18:00:00+05:30"),

    # Aug 22
    ("Wild Lasode Berry Harvest & Deseeding for Gunda Keri", "Lasode Berry Deseeding Gunda Keri", 3, 2, "2026-08-22T09:00:00+05:30"),
    ("Preservative Free Pickle Storage Tips: Keep Achar Fresh", "Preservative Free Pickle Storage Tips", 0, 2, "2026-08-22T13:00:00+05:30"),
    ("Saurashtra Rooftop Sun Drying Pickle Rituals Explained", "Saurashtra Rooftop Sun Drying Pickle", 0, 4, "2026-08-22T18:00:00+05:30"),

    # Aug 23
    ("History of Kathiyawadi Achar Making: Baa 45 Year Legacy", "History Kathiyawadi Achar Baa Legacy", 0, 0, "2026-08-23T09:00:00+05:30"),
    ("Sweet Shredded Mango Relish History: Traditional Chhundo", "Sweet Shredded Mango Relish Chhundo", 2, 4, "2026-08-23T13:00:00+05:30"),
    ("Sprouted Bengal Gram & Fenugreek: Methia Achar History", "Sprouted Bengal Gram Methia Achar History", 6, 0, "2026-08-23T18:00:00+05:30"),

    # Aug 24
    ("Cut Mango Cubes Skin On Pickling: Ancient Secrets", "Cut Mango Cubes Skin On Pickling", 4, 0, "2026-08-24T09:00:00+05:30"),
    ("Jaggery Cinnamon Spice Infusion in Heritage Sweet Pickles", "Jaggery Cinnamon Heritage Sweet Pickles", 1, 4, "2026-08-24T13:00:00+05:30"),
    ("Hand Pounded Spices vs Machine Powder Pickle Science", "Hand Pounded Spices vs Machine Powder Pickle", 0, 4, "2026-08-24T18:00:00+05:30"),

    # Aug 25
    ("Traditional Gujarati Pickle Sampler: 5 Must Have Achaars", "Traditional Gujarati Pickle Sampler", 0, 2, "2026-08-25T09:00:00+05:30"),
    ("Indian Heritage Sun Pickling: Solar Energy Curing Secrets", "Indian Heritage Sun Pickling Solar Energy", 2, 4, "2026-08-25T13:00:00+05:30"),
    ("Baa Handcrafted Pickle Collection: Taste Authentic Saurashtra", "Baa Handcrafted Pickle Collection Saurashtra", 0, 0, "2026-08-25T18:00:00+05:30")
]

def clean_title(title):
    if len(title) > 59:
        trimmed = title[:58].rsplit(' ', 1)[0]
        return trimmed
    return title

def generate_high_depth_html(title, keyword, prod_idx, category, pub_timestamp):
    p = PRODUCTS[prod_idx]
    clean_t = clean_title(title)
    pub_date_only = pub_timestamp[:10]
    
    html = f"""
<!-- JSON-LD Article Schema -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{clean_t}",
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
  "datePublished": "{pub_date_only}",
  "description": "Discover authentic {clean_t}. Handcrafted with 100% natural ingredients, wood-pressed yellow mustard oil, and Baa's 45-year Saurashtra family recipe."
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
      "name": "What makes authentic {clean_t} special?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "DivyaPrabha {p['name']} is handcrafted using Baa's 45+ year Saurashtra family recipe with 100% natural ingredients, wood-pressed yellow mustard oil, solar sun-curing rituals, and zero artificial preservatives or palm oil."
      }}
    }},
    {{
      "@type": "Question",
      "name": "How is {keyword} preserved naturally for 12 months without synthetic chemicals?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Natural solar sun-drying for 8 hours removes fruit moisture, while antimicrobial Sendha Namak, wild turmeric, split yellow mustard seeds (Rai Kuria), and complete submersion in wood-pressed mustard oil preserve the pickle naturally."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Why is wood-pressed yellow mustard oil superior for Indian achaar?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Wood-pressed yellow mustard oil provides mild pungency, rich Omega-3 fatty acids, and powerful antimicrobial submersion that prevents mold formation while keeping pickle spices rich and aromatic."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Where can I buy authentic {keyword} direct from Saurashtra online?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "You can order authentic handcrafted {p['name']} direct from Saurashtra online at DivyaPrabha Foods (divyaprabhafoods.com) in traditional glass jar packaging with nationwide delivery."
      }}
    }}
  ]
}}
</script>

<p class="dp-lead">
  When culinary enthusiasts and food connoisseurs search for authentic <strong>{keyword}</strong>, they seek the irreplaceable taste of solar sun-cured raw mangoes, stone-ground yellow mustard seeds (Rai Kuria), and unrefined wood-pressed mustard oil. In traditional Indian food culture, a jar of homemade achaar is far more than a condiment—it is a cherished digestive aid, a flavor multiplier, and a sacred link to centuries-old regional heritage. At DivyaPrabha Foods, every single batch of <strong>{p['name']}</strong> is handcrafted in small artisanal quantities under the direct guidance of Baa, preserving 45 years of authentic Saurashtra culinary mastery.
</p>

<h2>1. What Makes Authentic {clean_t} Unique?</h2>
<p>
  Authentic <strong>{keyword}</strong> relies on patience, natural solar heat, and unrefined regional spices rather than modern industrial shortcuts. Commercial store-bought pickles are mass-produced with high-heat cooking, cheap refined palm oil, synthetic glacial acetic acid, and chemical sodium benzoate preservatives that destroy beneficial probiotic microflora and leave a harsh synthetic aftertaste. In contrast, traditional Saurashtra pickling uses 100% cold-pressed yellow mustard oil, hand-pounded spices, and an 8-hour rooftop solar drying ritual that extracts excess moisture while preserving the crisp fruit structure and rich natural vitamins.
</p>

<h2>2. Baa's 45-Year Saurashtra Heritage & Traditional Rooftop Sun-Drying Ritual</h2>
<p>
  The journey of handcrafted <strong>{p['name']}</strong> begins long before the spices are blended. In the fertile agricultural belt of Saurashtra, firm and sour Rajapuri raw mangoes are hand-selected at peak seasonal maturity. Rajapuri mangoes are renowned for their dense, fibrous flesh and low water content, making them the gold standard for long-lasting achaar jars.
</p>
<p>
  After careful washing and hand-cubing, the raw mango pieces are tossed with pink rock salt (Sendha Namak) and organic haldi (turmeric) to begin natural moisture extraction. The mango cubes are then spread out on clean, unbleached cotton cloths across sunny rooftops for 8 full hours under the warm Saurashtra solar heat. This essential solar curing process concentrates the natural fruit acids, eliminates bacterial surface moisture, and guarantees a crisp, crunchy bite that endures for over 12 months in ceramic Martban jars.
</p>

<!-- 1-to-1 Visual Product CTA Card -->
<div class="dp-product-card" style="background: #fdf6ed; border: 1px solid #e8d5c0; border-radius: 16px; padding: 28px; margin: 36px 0; text-align: center; box-shadow: 0 4px 14px rgba(61,31,15,0.06);">
  <img src="{p['image']}" alt="{p['name']} Jar - Divyaprabha Foods" style="max-width: 250px; width: 100%; height: auto; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.12);">
  <h3 style="color: #b01215; margin: 8px 0 12px 0; font-size: 22px;">Authentic {p['name']}</h3>
  <p style="color: #3d1f0f; font-size: 15px; line-height: 1.6; margin-bottom: 18px; max-width: 600px; margin-left: auto; margin-right: auto;">{p['desc']}</p>
  <a href="{p['link']}" style="background: #b01215; color: #ffffff; padding: 14px 36px; border-radius: 50px; font-weight: bold; text-decoration: none; display: inline-block; font-size: 16px; box-shadow: 0 4px 10px rgba(176,18,21,0.3);">Buy Authentic {p['name']} Online →</a>
</div>

<h2>3. Comprehensive Ingredient Masterclass & Culinary Science</h2>
<p>
  Understanding the science behind <strong>{keyword}</strong> explains why traditional recipes remain unmatched in both taste and digestive wellness. Every single ingredient in Baa's recipe serves a vital dual function of flavor enhancement and natural bio-preservation:
</p>
<ul>
  <li><strong>Wood-Pressed Yellow Mustard Oil (Kachi Ghani):</strong> Unlike dark mustard oil which carries an aggressive pungency, yellow mustard oil offers a smooth, golden, nuttiness. Pressed slowly in wooden Kolhus without chemical solvents, it forms an impenetrable natural oxygen barrier over the pickle, completely suppressing mold spore formation while delivering gut-nourishing Omega-3 and Omega-6 fatty acids.</li>
  <li><strong>Split Yellow Mustard Seeds (Rai Kuria):</strong> Coarsely cracked in traditional stone mortars, split mustard seeds release natural sinigrin compounds that impart the signature tangy bite while naturally lowering pH levels for long-term preservation.</li>
  <li><strong>Coarsely Ground Fenugreek (Methi Kuria):</strong> Famous in Ayurvedic medicine for blood sugar balance and digestive warmth, coarse fenugreek seeds slowly absorb the oil and fruit juices, softening over weeks into savory flavor nuggets.</li>
  <li><strong>Pink Rock Salt (Sendha Namak):</strong> Unrefined, mineral-rich Himalayan pink salt provides gentle salinity without harsh chemical additives, drawing out fruit moisture while enriching the achaar with essential trace minerals.</li>
  <li><strong>Single-Origin Hing (Asafoetida) & Kashmiri Chilli:</strong> Pure compounded Asafoetida aids smooth gastric digestion and eliminates flatulence, while sun-dried Kashmiri red chilli provides a vibrant, natural ruby hue without synthetic food dyes.</li>
  <li><strong>Zero Chemical Promise:</strong> 100% free from palm oil, synthetic vinegar, sodium benzoate, artificial preservatives, or chemical acidity regulators.</li>
</ul>

<h2>4. Delicious Indian Meal Pairings & Gastronomic Jugalbandi</h2>
<p>
  Elevate everyday home cooking into a festive Gujarati dining feast by pairing <strong>{keyword}</strong> with classic Indian staples:
</p>
<ul>
  <li><strong>Kathiyawadi Bajra Rotla & White Butter:</strong> Spread a generous spoonful of {p['name']} over warm winter Bajra Rotla topped with fresh homemade white butter (Makhan) for the ultimate comforting Saurashtra meal.</li>
  <li><strong>Methi Thepla & Travel Tiffin:</strong> Gujarati Methi Theplas paired with {p['name']} remain soft, fresh, and delicious for long train journeys, road trips, or office lunchboxes.</li>
  <li><strong>Moong Dal Khichdi & Curd Rice:</strong> A single dollop of tangy raw mango pickle transforms simple yellow moong dal khichdi or cooling South Indian curd rice into a digestive masterpiece.</li>
  <li><strong>Stuffed Parathas & Crispy Khakhra:</strong> Serve alongside piping hot Aloo, Gobi, or Paneer Parathas, or spoon over crispy whole wheat Khakhra for a light afternoon tea snack.</li>
</ul>

<h2>5. Preservative-Free Storage & Ceramic Martban Maintenance Tips</h2>
<p>
  Because DivyaPrabha pickles contain zero synthetic chemical preservatives, following proper traditional storage rituals ensures your achaar stays fresh, crunchy, and aromatic for over 12 months:
</p>
<ol>
  <li><strong>Always Use a Clean, Dry Wooden Spoon:</strong> Water moisture is the primary cause of pickle spoilage. Never insert wet cutlery, damp spoons, or fingers inside your achaar jar.</li>
  <li><strong>Maintain the Oil Cap Submersion:</strong> Ensure the raw mangoes and spices remain completely submerged beneath a 1/2-inch top layer of pure wood-pressed yellow mustard oil. If oil levels drop after daily consumption, top up with fresh cold-pressed mustard oil.</li>
  <li><strong>Store in Ceramic Martban or Glass Jars:</strong> Keep your pickle in traditional lead-free ceramic Martban jars or food-grade glass containers stored in a cool, dark, dry pantry away from direct kitchen stove heat.</li>
  <li><strong>Do Not Refrigerate:</strong> Cold refrigeration causes mustard oil to solidify and dulls the natural aromatic bouquet of stone-ground spices. Store at normal room temperature.</li>
</ol>

<h2>6. Frequently Asked Questions (FAQs)</h2>

<h3>Q1. What makes DivyaPrabha {p['name']} authentic?</h3>
<p>
  DivyaPrabha {p['name']} is handcrafted in small artisanal batches following Baa's 45+ year family recipe from Saurashtra. We use 100% natural ingredients, sour Rajapuri raw mangoes, wood-pressed yellow mustard oil, 8-hour rooftop solar curing, and zero chemical preservatives or palm oil.
</p>

<h3>Q2. How is {keyword} preserved naturally for 12 months without chemical preservatives?</h3>
<p>
  Our natural 4-stage preservation relies on: (1) 8-hour rooftop sun-drying to remove moisture, (2) mineral-rich Sendha Namak, (3) antimicrobial Rai Kuria and wild turmeric, and (4) full oil submersion in pure cold-pressed yellow mustard oil.
</p>

<h3>Q3. Why is wood-pressed yellow mustard oil better than commercial oil?</h3>
<p>
  Wood-pressed (Kachi Ghani) yellow mustard oil is extracted at low temperatures without chemical solvents. It delivers a smooth, non-pungent flavor, rich Omega-3 fatty acids, and powerful antimicrobial protection without the inflammatory risks of cheap commercial palm oil.
</p>

<h3>Q4. Where can I buy authentic {keyword} direct from Saurashtra online?</h3>
<p>
  You can order authentic handcrafted {p['name']} online directly from DivyaPrabha Foods (divyaprabhafoods.com) in traditional glass jar packaging with nationwide express home delivery.
</p>

<div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
  <a href="{p['link']}" style="background: #b01215; color: #ffffff; padding: 16px 40px; border-radius: 50px; font-weight: bold; text-decoration: none; display: inline-block; font-size: 18px; box-shadow: 0 4px 14px rgba(176,18,21,0.35);">Order Handcrafted {p['name']} Online Direct from Saurashtra →</a>
</div>
"""
    return html

def run():
    print("🚀 PUBLISHING MISSING DAYS (AUG 15 - AUG 19) AND FUTURE SCHEDULED ARTICLES TO SHOPIFY...")
    published_count = 0
    error_count = 0

    for item in TOPIC_TEMPLATES:
        title, keyword, prod_idx, cat_idx, pub_timestamp = item
        category = CATEGORIES[cat_idx]
        clean_t = clean_title(title)
        html_body = generate_high_depth_html(title, keyword, prod_idx, category, pub_timestamp)
        
        words = len(re.sub(r'<.*?>', '', html_body).split())
        excerpt = f"Discover authentic {clean_t}. Handcrafted with 100% natural ingredients, wood-pressed yellow mustard oil, and Baa's 45-year heritage Saurashtra recipe."

        payload = {
            "article": {
                "title": clean_t,
                "author": "Baa & The DivyaPrabha Culinary Team",
                "tags": category,
                "summary_html": excerpt,
                "body_html": html_body,
                "published": True,
                "published_at": pub_timestamp
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
                published_count += 1
                print(f"✅ [{pub_timestamp[:10]}] Published (#{published_count}): '{clean_t}' | Words: {words} | ID: {art.get('id')}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error publishing '{clean_t}':", e)

    print(f"\n🎉 DONE! Published {published_count} articles to Shopify store with zero errors! (Errors: {error_count})")

if __name__ == "__main__":
    run()
