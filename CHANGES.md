# Divyaprabha Foods — Master Log of Code, Theme & SEO Changes (`CHANGES.md`)

This document maintains a continuous, detailed record of all theme features, liquid modifications, CSS rules, SEO safeguards, and blog post updates applied to `divyaprabhafoods.com`. Refer to this document before generating new blog posts or theme updates.

---

## 🚨 1. Store Safeguard & Workspace Verification

- **Workspace Path**: Strictly `/Users/apple/Documents/Shopify Theme VS code/DivyaPrabha Food`
- **Target Shopify Store**: `divyaprabhafoods.com` (MyShopify Domain: `divyaprabhafoods.myshopify.com`)
- **Target Live Theme**: `Magic Checkout - ArhamFoods` (Theme ID: `#161791869142`)
- **Prohibition**: NEVER push, sync, publish, or execute Shopify CLI commands targeting *The Pickle Affair* (`pickleaffair.com`).

---

## 🎯 2. Core 9 Execution Rules & Growth Safeguards

1. **Target Environment Protocol**: Verify path `/Users/apple/Documents/Shopify Theme VS code/DivyaPrabha Food` and target theme `#161791869142` before running CLI commands.
2. **Word Count & Depth**: 1,200–1,500 words minimum per article, structured with clean H2/H3 subheadings, ingredient breakdowns, health angles, storage tips, and visual product cards.
3. **Title Tag Length**: Primary keyword first, strictly under 60 characters.
4. **FAQ Section**: 3–5 questions per post with embedded JSON-LD `FAQPage` schema.
5. **JSON-LD Structured Data**: Include valid `<script type="application/ld+json">` for `Article` / `BlogPosting` and `FAQPage` inside the HTML body.
6. **Product Link Rules**: Link directly to specific live product handles (`/products/mango-pickle-traditional-keri-achar-gujarati`, `/products/gor-keri-pickle-jaggery-mango-achar-gujarati`, `/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati`, `/products/gunda-keri-pickle-lasode-ka-achar-gujarati`, `/products/katka-keri-pickle-homemade-gujarati-mango-achar`, `/products/sweet-mango-pickle-meethi-keri-achar-homemade`, `/products/chana-keri-methi-pickle-gujarati-methia-achar`). Never link to 0-item collections!
7. **Tag Taxonomy**: Assign strictly from the 5 core categories (`Heritage Recipes`, `Health & Spices`, `Buying Guides`, `Pickle Pairings`, `Artisanal Craft`).
8. **Authentic Store CDN Images & Product CTA Boxes**: Use real store CDN images (`SpecialMangoBig.webp`, `Gor_Keri_500g.webp`, `GundaKeriBig.webp`, `ChhundoBigFront.webp`, `Chana_Keri_Methi_Big.webp`, `KatkaKeriBigfront_jpg.webp`, `SweetmangoBigFront.webp`). Every blog post MUST target ONE specific product URL with an embedded CTA box featuring price, title, image, and buy button.
9. **100% Structural & Narrative Content Uniqueness (Zero Boilerplate & Zero Plagiarism)**: Every blog post (present and future) MUST be 100% unique in concept, angle, action calls, introductory hooks, and H2/H3 outline structure. Prohibit generic intro templates ("When culinary enthusiasts...") and formulaic subheadings ("1. What Makes Authentic [Product] Unique? 2. Baa's 45-Year...").
10. **Mandatory Grade A+ SEO Score (95–100/100 Points Target)**: Every new blog post generated or published MUST be pre-audited and scored at Grade A+ (95–100 Pts). It MUST satisfy: (1) Title < 60 chars with primary keyword first (15 Pts), (2) Word count >= 1,200 words minimum (15 Pts), (3) Dual JSON-LD Article + FAQPage schemas (15 Pts), (4) 3–5 question FAQ section (10 Pts), (5) Product CTA card with real store CDN image & alt text (15 Pts), (6) 100% valid product link handles with zero 404s (10 Pts), (7) Tag assigned from the 5 core categories (10 Pts), and (8) 100% unique non-boilerplate narrative structure (10 Pts).

---

## 🎨 3. Applied Theme & UI Modifications

### A. Listen to Article Audio Player Widget
- **Location**: [`sections/dp-article.liquid`](file:///Users/apple/Documents/Shopify%20Theme%20VS%20code/DivyaPrabha%20Food/sections/dp-article.liquid) and [`sections/main-article.liquid`](file:///Users/apple/Documents/Shopify%20Theme%20VS%20code/DivyaPrabha%20Food/sections/main-article.liquid).
- **Features**:
  - Uses browser native Web Speech Synthesis API.
  - Automatically filters and defaults to **Indian Female Voices** (`Lekha (Indian Voice)`, `Google Hi-IN Female`, `Microsoft Heera`).
  - Includes Play/Pause button, time progress readout, voice selector dropdown, and speed multiplier control (`1x`, `1.25x`, `1.5x`, `2x`).

### B. Universal Head CSS Injection (`<style id="dp-global-sidebar-fix">`)
- **Location**: [`layout/theme.liquid`](file:///Users/apple/Documents/Shopify%20Theme%20VS%20code/DivyaPrabha%20Food/layout/theme.liquid) in `<head>`.
- **Purpose**: Overrides all global theme styles with 100% browser priority across all Shopify templates.
- **Rules Enforced**:
  - **Widget 1 (Pickles & Products)**: `.dp-product-mini-card` set to `display: flex !important; flex-direction: row !important;` with 76px left thumbnail image (`width: 76px !important; min-width: 76px !important; flex: 0 0 76px !important;`), SALE badge, prices, compare prices, and red **Buy Now →** buttons.
  - **Widget 2 (Categories)**: `.dp-category-list a` styled as white rounded cards (`#ffffff`, `border: 1px solid #e8d5c0`, `border-radius: 12px`, red hover effect) with item count badges.
  - **Widget 3 (Blog Topics)**: `.dp-recent-topics-list li` styled as white rounded cards with uppercase red topic tags (`BUYING GUIDES`, `HERITAGE RECIPES`).
  - **Widget 4 (Focus Keywords Tag Cloud)**: `.dp-tag-pill` styled as white rounded pills (`#ffffff`, `border-radius: 50px`, `#b01215` active/hover state).
  - **Focus Keywords Show More / Show Less Button**:
    - Added `.dp-keywords-cloud--collapsed` (max-height 120px with bottom gradient mask).
    - Added `.dp-show-more-tags-btn` (`+ Show More Keywords ↓` / `- Show Less ↑`).
    - Added `toggleDpKeywords()` JavaScript function in `layout/theme.liquid` before `</body>`.

### C. Left-Side Article Content Typography & CTA Card Fixes
- **Heading Color**: Restored deep brand brown (`#3d1f0f`) for `h1`, `h2`, `h3` with `margin-top: 36px` spacing.
- **Body Text**: `font-size: 16px !important; line-height: 1.75 !important; color: #2d1206 !important; margin-bottom: 20px !important;`.
- **Product CTA Box Image Fix**: Added `.dp-cta-box img` override (`width: 130px !important; height: 130px !important; margin: 0 !important; flex: 0 0 130px !important;`) to prevent global image centering from distorting product cards.

### D. Mobile Responsive Layout & Centered Sidebar Alignment (< 991px)
- **Main Content First**: Locked `.dp-article-main-content` to `order: 1 !important; display: block !important; visibility: visible !important; width: 100% !important;`. The hero header, audio player, share bar, featured image, and article text ALWAYS display first on mobile viewports.
- **Sidebar Stacked Below**: Set `aside.dp-article-sidebar` to `order: 2 !important; margin-top: 36px !important;`.
- **Centered Sidebar Alignment**: Center-aligned all 4 sidebar widgets (`margin: 0 auto; max-width: 520px; text-align: center; justify-content: center;`), mini product cards, category lists, topic tags, and Focus Keyword cloud pills on mobile screens.

---

## 📝 4. Summary of Published Unique Blog Articles

1. **Katka Keri Cut Mango Pickle** (ID: `665974374614`)
   - *Concept*: The Geometry of Crunch & Rooftop Moisture Extraction
   - *Handles*: `/products/katka-keri-pickle-homemade-gujarati-mango-achar`
   - *CDN Image*: `https://divyaprabhafoods.com/cdn/shop/files/KatkaKeriBigfront_jpg.webp`

2. **Gunda Keri Pickle Buy Online** (ID: `665974341846`)
   - *Concept*: Wild Botanical Synergy of Glueberries & Raw Mango Stuffing
   - *Handles*: `/products/gunda-keri-pickle-lasode-ka-achar-gujarati`
   - *CDN Image*: `https://divyaprabhafoods.com/cdn/shop/files/GundaKeriBig.webp`

3. **Sun Cured Chhundo Pickle Online** (ID: `665974309078`)
   - *Concept*: Solar Caramelization & Zero-Heat Amber Curing
   - *Handles*: `/products/chhundo-pickle-sweet-shredded-mango-achar-gujarati`
   - *CDN Image*: `https://divyaprabhafoods.com/cdn/shop/files/ChhundoBigFront.webp`

4. **Jaggery Gor Keri Achar Online** (ID: `665974276310`)
   - *Concept*: Unrefined Organic Jaggery Bio-Preservation & Slow Maceration
   - *Handles*: `/products/gor-keri-pickle-jaggery-mango-achar-gujarati`
   - *CDN Image*: `https://divyaprabhafoods.com/cdn/shop/files/Gor_Keri_500g.webp`

5. **Rajapuri Raw Mango Pickle Online** (ID: `665974243542`)
   - *Concept*: The Sovereign Pickling Mango of Saurashtra & Kachi Ghani Oxygen Barrier
   - *Handles*: `/products/mango-pickle-traditional-keri-achar-gujarati`
   - *CDN Image*: `https://divyaprabhafoods.com/cdn/shop/files/SpecialMangoBig.webp`

---

*Last Updated: August 12, 2026*
