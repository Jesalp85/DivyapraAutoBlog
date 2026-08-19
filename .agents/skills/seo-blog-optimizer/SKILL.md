---
name: seo-blog-optimizer
description: Universal SEO, GEO/AEO (AI Search), E-E-A-T, and Schema optimization skill for Divyaprabha Foods. Combines the 200k Impression / 50k Click Growth Playbook with Claude-SEO sub-agent standards.
---

# 🚀 Universal SEO & GEO Blog Optimizer — Divyaprabha Foods

Use this skill whenever creating, auditing, or optimizing blog posts for Divyaprabha Foods to achieve **1st-page Google rankings**, win **Google AI Overviews (GEO/AEO)**, eliminate 404 links, and drive D2C sales conversions.

---

## 🤖 1. AI Search & Generative Engine Optimization (GEO/AEO)

To win citations in **Google AI Overviews, Gemini, ChatGPT, Perplexity, and PAA boxes**:
- **Citability Answer Blocks:** Place a 134–167 word self-contained direct answer block right under the main `<h2>` heading in the first 2 sentences.
- **Question-Based Heading Hierarchy:** Phrase `<h2>` and `<h3>` headings as exact natural language questions user type (e.g. *"What makes traditional Saurashtra mango pickle different?"*).
- **Entity & Citation Density:** Explicitly mention verified entities: `Rajapuri Raw Mangoes`, `Saurashtra`, `Kathiyawad`, `Wood-Pressed Yellow Mustard Oil`, `Sendha Namak (Pink Rock Salt)`, `Baa's Heritage Recipe`.

---

## 🏆 2. Google E-E-A-T & Quality Rater Guidelines

Every article must reflect authentic **Experience, Expertise, Authoritativeness, and Trustworthiness**:
- **Experience (First-Hand Proof):** Highlight Baa's 45+ years of handcrafting pickles in Saurashtra, rooftop 8-hour sun-drying rituals, and traditional ceramic jar (Martban) curing.
- **Expertise & Transparency:** Document spice grinding techniques (coarse Rai Kuria & Methi Kuria) and oil submersion methods.
- **Trustworthiness:** Transparent ingredients (zero synthetic vinegar, zero palm oil, zero sodium benzoate), verified store address, and authentic Shopify CDN jar images.

---

## 📈 3. SEO Growth Playbook Levers (200k Impressions & 50k Clicks)

| Element | Requirement / Constraint | Technical Implementation |
| :--- | :--- | :--- |
| **Primary Title (SERP)** | **Capped strictly at 55–60 characters** | Primary keyword placed first; no truncation in SERPs or social previews. |
| **Meta Description** | **150–160 characters** | High-clickthrough teaser with primary & secondary keywords + call-to-action. |
| **Header Hierarchy** | **Single `<h1>` per page** | Page title as H1; logical `<h2>` section headings and `<h3>` sub-points. |
| **Word Count & Depth** | **1,200–1,500 words minimum** | Comprehensive coverage: culinary history, health angles, storage tips, FAQs. |
| **Store Product Images & CTAs** | **Authentic Store Product CDN Images** | Use official Divyaprabha product CDN images matching exact store jars + embed 1-to-1 targeted product CTA boxes (`/products/<handle>`) with SEO `alt` text. |
| **Internal Linking** | **100% Valid Product Handles** | Direct links to `/products/<valid-handle>` (ZERO 404 links). |
| **Structured Data** | **Embedded JSON-LD** | Valid `<script type="application/ld+json">` for `Article` & `FAQPage` schema. |
| **Tag Taxonomy** | **5 Core Categories Only** | `Heritage Recipes`, `Health & Spices`, `Buying Guides`, `Pickle Pairings`, `Artisanal Craft`. |

---

## 🛍️ 4. Divyaprabha Foods — Live Product Handle & CDN Image Registry

Always map product recommendations and CTA buttons to these **verified live store handles and CDN images**:

1. **Homemade Mango Pickle | Aam Ka Achar**
   - **Handle:** `mango-pickle-traditional-keri-achar-gujarati`
   - **Link:** `/products/mango-pickle-traditional-keri-achar-gujarati`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SpecialMangoBig.webp?v=1782721972`

2. **Gor Keri | Jaggery Mango Achar**
   - **Handle:** `gor-keri-pickle-jaggery-mango-achar-gujarati`
   - **Link:** `/products/gor-keri-pickle-jaggery-mango-achar-gujarati`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Gor_Keri_500g.webp?v=1784831601`

3. **Chhundo | Sweet Shredded Mango Achar**
   - **Handle:** `chhundo-pickle-sweet-shredded-mango-achar-gujarati`
   - **Link:** `/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/ChhundoBigFront.webp?v=1782723201`

4. **Methia Keri | Chana Keri Methi Achar**
   - **Handle:** `chana-keri-methi-pickle-gujarati-methia-achar`
   - **Link:** `/products/chana-keri-methi-pickle-gujarati-methia-achar`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Chana_Keri_Methi_Big.webp?v=1782722238`

5. **Gunda Keri | Lasode Ka Achar**
   - **Handle:** `gunda-keri-pickle-lasode-ka-achar-gujarati`
   - **Link:** `/products/gunda-keri-pickle-lasode-ka-achar-gujarati`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/GundaKeriBig.webp?v=1782723036`

6. **Katka Keri Pickle | Homemade Gujarati Mango Achar**
   - **Handle:** `katka-keri-pickle-homemade-gujarati-mango-achar`
   - **Link:** `/products/katka-keri-pickle-homemade-gujarati-mango-achar`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/KatkaKeriBigfront_jpg.webp?v=1784704467`

7. **Meethi Keri | Sweet Mango Achar**
   - **Handle:** `sweet-mango-pickle-meethi-keri-achar-homemade`
   - **Link:** `/products/sweet-mango-pickle-meethi-keri-achar-homemade`
   - **Image:** `https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SweetmangoBigFront.webp?v=1782722922`

---

## 🏗️ 5. Standard HTML & JSON-LD Schema Architecture

```html
<!-- 1. JSON-LD Article Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Primary Keyword Title <= 60 chars]",
  "author": {
    "@type": "Organization",
    "name": "Baa & The DivyaPrabha Culinary Team"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Divyaprabha Foods",
    "logo": {
      "@type": "ImageObject",
      "url": "https://divyaprabhafoods.com/cdn/shop/files/logo.png"
    }
  },
  "datePublished": "2026-08-09",
  "description": "[Meta Description 150-160 chars]"
}
</script>

<!-- 2. JSON-LD FAQPage Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 1]"
      }
    }
  ]
}
</script>

<!-- 3. Visual Product Card Component -->
<div class="dp-product-card" style="background: #fdf6ed; border: 1px solid #e8d5c0; border-radius: 16px; padding: 24px; margin: 32px 0; text-align: center; box-shadow: 0 4px 12px rgba(61,31,15,0.05);">
  <img src="[SHOPIFY_CDN_IMAGE_URL]" alt="[PRODUCT_NAME] Jar - Divyaprabha Foods" style="max-width: 240px; width: 100%; height: auto; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
  <h3 style="color: #b01215; margin: 8px 0 12px 0; font-size: 20px;">[PRODUCT_TITLE]</h3>
  <p style="color: #3d1f0f; font-size: 14px; margin-bottom: 16px;">100% Handcrafted in Saurashtra with Cold-Pressed Yellow Mustard Oil & Natural Spices.</p>
  <a href="[VALID_PRODUCT_LINK]" style="background: #b01215; color: #ffffff; padding: 12px 32px; border-radius: 50px; font-weight: bold; text-decoration: none; display: inline-block;">Buy Authentic [PRODUCT_NAME] Online →</a>
</div>
```
