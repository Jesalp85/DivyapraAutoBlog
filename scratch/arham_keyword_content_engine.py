#!/usr/bin/env python3
"""
Divyaprabha Foods — Arham keyword blog + collection engine

Continuous (no end date):
  - Blogs: 3/day at random IST times, forever (cycles Excel keywords + angles)
  - Collections: 2/week, forever (new keyword-led collection pages)

- Reads scratch/arham_focus_keywords.json (from Excel)
- Creates unique SEO blog articles (1200+ words HTML) mapped to live products
- Creates SEO collection pages for product pillars, combos, and keyword themes
- Re-run safely; skips existing Shopify handles

Usage:
  export SHOPIFY_ACCESS_TOKEN=shpat_xxx
  python3 scratch/arham_keyword_content_engine.py --status
  python3 scratch/arham_keyword_content_engine.py --blogs --ongoing --limit 3
  python3 scratch/arham_keyword_content_engine.py --collections --ongoing --collection-limit 2
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "scratch" / "arham_focus_keywords.json"
STATE_PATH = ROOT / "scratch" / "arham_keyword_engine_state.json"

SHOP_URL = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
BLOG_ID = int(os.environ.get("SHOPIFY_BLOG_ID", "97942077654"))
API = "2024-04"
CTX = ssl.create_default_context()
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

PRODUCTS = {
    "special_mango": {
        "name": "Homemade Mango Pickle | Aam Ka Achar",
        "handle": "mango-pickle-traditional-keri-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SpecialMangoBig.webp?v=1782721972",
        "desc": "Handcrafted Rajapuri raw mango achar in wood-pressed yellow mustard oil.",
    },
    "sweet_mango": {
        "name": "Meethi Keri | Sweet Mango Achar",
        "handle": "sweet-mango-pickle-meethi-keri-achar-homemade",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/SweetmangoBigFront.webp?v=1782722922",
        "desc": "Mildly spiced sweet raw mango slices matured with natural jaggery.",
    },
    "gor_keri": {
        "name": "Gor Keri | Jaggery Mango Achar",
        "handle": "gor-keri-pickle-jaggery-mango-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Gor_Keri_500g.webp?v=1784831601",
        "desc": "Sugar-free sweet mango pickle with organic jaggery and Kashmiri chilli.",
    },
    "chana_keri": {
        "name": "Methia Keri | Chana Keri Methi Achar",
        "handle": "chana-keri-methi-pickle-gujarati-methia-achar",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Chana_Keri_Methi_Big.webp?v=1782722238",
        "desc": "Protein-rich chickpea fenugreek mango pickle from Saurashtra kitchens.",
    },
    "gunda_keri": {
        "name": "Gunda Keri | Lasode Ka Achar",
        "handle": "gunda-keri-pickle-lasode-ka-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/GundaKeriBig.webp?v=1782723036",
        "desc": "Wild glueberries stuffed with shredded Rajapuri mango and mustard kuria.",
    },
    "chhundo": {
        "name": "Chhundo | Sweet Shredded Mango Achar",
        "handle": "chhundo-pickle-sweet-shredded-mango-achar-gujarati",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/ChhundoBigFront.webp?v=1782723201",
        "desc": "Sun-cured shredded mango relish caramelized under Saurashtra heat.",
    },
    "katka": {
        "name": "Katka Keri Pickle | Homemade Gujarati Mango Achar",
        "handle": "katka-keri-pickle-homemade-gujarati-mango-achar",
        "image": "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/KatkaKeriBigfront_jpg.webp?v=1784704467",
        "desc": "Crunchy cut mango cubes cured in kachi ghani mustard oil.",
    },
}

PILLAR_PRODUCT = {
    "Special Mango": "special_mango",
    "Sweet Mango": "sweet_mango",
    "Gor-Keri": "gor_keri",
    "Chana Keri": "chana_keri",
    "Gunda Keri": "gunda_keri",
    "Aachar Masala": "chana_keri",  # closest live product for CTA
    "Sweet Lemon": "special_mango",  # no lemon SKU yet; CTA to flagship mango
    "Sweet Combo": "gor_keri",
    "Tangy Combo": "gunda_keri",
    "6 Combo": "special_mango",
}

CATEGORIES = [
    "Heritage Recipes",
    "Health & Spices",
    "Buying Guides",
    "Pickle Pairings",
    "Artisanal Craft",
]

ANGLE_H2 = {
    "heritage": [
        "How did Saurashtra households preserve {kw} for generations?",
        "What rooftop sun-drying ritual shapes authentic {kw}?",
        "Which spices define Baa's traditional {kw} masala?",
        "How should you store glass-jar {kw} for twelve months?",
    ],
    "health": [
        "Is traditionally made {kw} better for digestion than factory pickle?",
        "Why does wood-pressed mustard oil matter in {kw}?",
        "What natural preservatives keep {kw} free of synthetic vinegar?",
        "How can you serve {kw} as part of a balanced Gujarati thali?",
    ],
    "buy": [
        "What should you check before you buy {kw} online?",
        "How do homemade {kw} jars differ from supermarket pickles?",
        "Which jar size of {kw} suits daily family use?",
        "How does Divyaprabha Foods ship authentic {kw} across India?",
    ],
    "pairing": [
        "What meals pair best with authentic {kw}?",
        "How do Kathiyawadi kitchens use {kw} beyond thepla?",
        "Can {kw} work with rice, dal, and travel tiffins?",
        "What serving tips keep the crunch of {kw} intact?",
    ],
    "craft": [
        "How is small-batch {kw} prepared without industrial shortcuts?",
        "Why do Rajapuri mangoes elevate premium {kw}?",
        "What role does Sendha Namak play in curing {kw}?",
        "How do ceramic Martban jars protect the aroma of {kw}?",
    ],
}


def require_token():
    if not TOKEN or TOKEN.startswith("os.environ"):
        raise SystemExit(
            "❌ Set SHOPIFY_ACCESS_TOKEN in your environment first.\n"
            "   export SHOPIFY_ACCESS_TOKEN='shpat_...'"
        )


def api(method: str, path: str, payload=None):
    url = f"{SHOP_URL}/admin/api/{API}/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"{method} {path} -> {e.code}: {err[:500]}") from e


def load_registry():
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return data


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"blog_handles": {}, "collection_handles": {}, "scheduled_slots": []}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:70].strip("-") or "pickle-guide"


def clean_title(title: str) -> str:
    if len(title) <= 59:
        return title
    return title[:58].rsplit(" ", 1)[0]


def pick_angle(keyword: str, salt: str = "") -> str:
    h = int(hashlib.md5(f"{keyword.lower()}|{salt}".encode()).hexdigest(), 16)
    return list(ANGLE_H2.keys())[h % len(ANGLE_H2)]


def map_product(pillar: str | None, keyword: str):
    if pillar and pillar in PILLAR_PRODUCT:
        return PRODUCTS[PILLAR_PRODUCT[pillar]]
    kl = keyword.lower()
    if "gor" in kl or "jaggery" in kl or "gorkeri" in kl:
        return PRODUCTS["gor_keri"]
    if "gunda" in kl or "lasod" in kl:
        return PRODUCTS["gunda_keri"]
    if "chana" in kl or "methi" in kl or "methia" in kl:
        return PRODUCTS["chana_keri"]
    if "chhundo" in kl or "shred" in kl:
        return PRODUCTS["chhundo"]
    if "katka" in kl:
        return PRODUCTS["katka"]
    if "sweet" in kl or "meethi" in kl or "mitha" in kl:
        return PRODUCTS["sweet_mango"]
    return PRODUCTS["special_mango"]


def build_article_html(
    keyword: str,
    pillar: str | None,
    pub_date: str,
    angle: str | None = None,
    handle_suffix: str = "",
) -> tuple[str, str, str, dict]:
    prod = map_product(pillar, keyword)
    angle = angle or pick_angle(keyword, handle_suffix or pub_date)
    h2s = [h.format(kw=keyword) for h in ANGLE_H2[angle]]
    title_variants = [
        f"{keyword}: Gujarati Homemade Achar Guide",
        f"{keyword} Homemade Achar",
        f"Buy {keyword} | Saurashtra Achar Guide",
        f"{keyword} — Traditional Kathiyawadi Pickle",
        f"Authentic {keyword} from Divyaprabha Foods",
    ]
    title = clean_title(title_variants[int(hashlib.md5(f"{keyword}|{angle}|{handle_suffix}".encode()).hexdigest(), 16) % len(title_variants)])
    category = CATEGORIES[int(hashlib.md5(keyword.encode()).hexdigest(), 16) % len(CATEGORIES)]
    handle = slugify(f"{keyword}-{angle}-{handle_suffix}" if handle_suffix else f"{keyword}-{angle}")

    faq = [
        (
            f"What is authentic {keyword}?",
            f"Authentic {keyword} from Divyaprabha Foods follows Baa's Saurashtra method: solar moisture extraction, Sendha Namak, hand-pounded mustard kuria, and wood-pressed yellow mustard oil — without synthetic vinegar or palm oil.",
        ),
        (
            f"How long does homemade {keyword} last?",
            f"When submerged fully in wood-pressed mustard oil and stored in a cool dry place with a dry spoon, glass-jar {keyword} stays aromatic for 12+ months.",
        ),
        (
            f"Where can I buy {keyword} online in India?",
            f"Order {prod['name']} at Divyaprabha Foods with nationwide delivery. Each jar is packed for freshness and traditional Kathiyawadi flavour.",
        ),
        (
            f"Is {keyword} made without preservatives?",
            "Yes. Preservation comes from sun-curing, rock salt, turmeric, mustard seed enzymes, and oil submersion — not sodium benzoate or industrial acetic acid.",
        ),
    ]

    # Varied lead paragraphs (avoid banned generic boilerplate)
    leads = {
        "heritage": f"Across Kathiyawad courtyards, summer still smells of rooftop cloths lined with salted mango and the quiet patience behind <strong>{keyword}</strong>. At Divyaprabha Foods, that same Saurashtra discipline — not factory haste — shapes every jar linked to <strong>{prod['name']}</strong>.",
        "health": f"Shoppers comparing gut-friendly condiments often ask whether <strong>{keyword}</strong> can stay bold without synthetic vinegar. Divyaprabha Foods answers with solar curing, Sendha Namak, and wood-pressed mustard oil in small batches of <strong>{prod['name']}</strong>.",
        "buy": f"Searching <strong>{keyword}</strong> online should end in a jar you can trust: readable ingredients, glass packaging, and a recipe older than supermarket shortcuts. Divyaprabha Foods ships <strong>{prod['name']}</strong> for that exact expectation.",
        "pairing": f"From methi thepla to travel tiffins, Gujarati tables treat <strong>{keyword}</strong> as a flavour anchor. Divyaprabha Foods bottles that everyday utility in <strong>{prod['name']}</strong>, cured for crunch and aroma.",
        "craft": f"Small-batch <strong>{keyword}</strong> is measured by hand cuts, spice coarseness, and oil clarity — details industrial lines skip. Baa's process for <strong>{prod['name']}</strong> keeps those craft marks intact.",
    }

    sections = []
    extra_blocks = {
        "heritage": (
            f"<p>In village kitchens around Junagadh and Amreli, women still argue gently about mango cut size and oil temperature when preparing {keyword}. "
            f"Those debates are not nostalgia — they control water activity and spice bloom. Divyaprabha Foods documents the same decisions so urban buyers receive "
            f"a jar that tastes like a Saurashtra summer courtyard, not a canteen tray.</p>"
            f"<p>Heritage also means refusing shortcuts: no caramel colour, no soft-fruit puree from overripe stock, no reheating in industrial kettles that flatten aroma. "
            f"When you open <strong>{prod['name']}</strong>, you should smell mustard and fruit first, then chilli warmth — never solvent-like tang.</p>"
        ),
        "health": (
            f"<p>People exploring {keyword} for lighter meals still want bold flavour. Traditional achaar supports that goal when it avoids refined sugar dumps and palm oil. "
            f"Mustard oil’s natural pungency and spice polyphenols give satisfaction in teaspoon amounts, which helps portions stay modest on everyday plates.</p>"
            f"<p>This is not medical advice — it is culinary common sense from Kathiyawadi homes that used pickle as appetite cue and digestive companion beside bajra and dal. "
            f"Divyaprabha Foods keeps ingredient lists short so you can judge {keyword} with clear eyes.</p>"
        ),
        "buy": (
            f"<p>Online marketplace listings for {keyword} often recycle stock photos and vague ‘homemade’ claims. Ask for jar material, oil type, mango variety, and FSSAI identity. "
            f"Divyaprabha Foods publishes product pages with real CDN jar images and direct handles so you land on the exact SKU, not a dead collection.</p>"
            f"<p>Compare shipping temperature notes for summer months, and prefer sellers who pack glass with cushioning. A cracked jar ruins more than money — it wastes a seasonal cure.</p>"
        ),
        "pairing": (
            f"<p>Think of {keyword} as a seasoning layer: a little on the edge of a thepla, stirred into plain dahi, or beside aloo sabzi when lunch feels flat. "
            f"Sweet styles lift bitter greens; tangy mustard-forward styles cut through oily snacks. Gujarati hosts often place two pickles on the table so guests can choose intensity.</p>"
            f"<p>For office tiffins, pack pickle separately so steam does not soften rotis. For travel, choose well-sealed glass and keep upright. These habits protect the craft inside the jar.</p>"
        ),
        "craft": (
            f"<p>Craft shows up in spice grind size. Too fine and {keyword} turns pasty; too coarse and raw seed bitterness dominates. Baa’s kuria sits in the middle — audible crunch, even coating. "
            f"Fruit pieces are cut for spoonability, not for factory chute speed.</p>"
            f"<p>Oil clarification and resting time after packing also matter. Rushing to ship wet, unsettled jars creates cloudy brine and muted aroma. Patience is part of the recipe.</p>"
        ),
    }

    for i, h2 in enumerate(h2s):
        sections.append(f"<h2>{h2}</h2>")
        if i == 0:
            sections.append(
                f"<p>{keyword} becomes memorable when fruit moisture is pulled under Saurashtra sun before spices go in. "
                f"Rajapuri-style mango character, pink rock salt, and wild turmeric begin the cure; split yellow mustard "
                f"(Rai Kuria) and fenugreek (Methi Kuria) follow. The result is layered heat without chemical sharpness.</p>"
            )
            sections.append(
                f"<p>Divyaprabha Foods keeps batches small so <strong>{prod['name']}</strong> retains bite and perfume. "
                f"That is the practical difference between heritage {keyword} and mass-produced pickle cooked in palm oil.</p>"
            )
            sections.append(extra_blocks[angle])
        elif i == 1:
            sections.append(
                f"<p>Wood-pressed yellow mustard oil coats every piece, blocking air while carrying spice oils into the fruit. "
                f"Unlike cheap refined oils, kachi ghani mustard stays pungent and stable in Indian kitchens. Combined with "
                f"Sendha Namak, it supports a twelve-month pantry life for {keyword} when spoons stay dry.</p>"
            )
            sections.append(
                f"<p>Spice sequencing matters: turmeric early for colour and antimicrobial lift, chilli for warmth, asafoetida in restrained pinches for savoury depth. "
                f"Each addition is tasted against the fruit’s natural sourness so {keyword} stays balanced rather than loud for the sake of loudness.</p>"
            )
            sections.append(
                f"""
<div class="dp-product-card" style="background:#fdf6ed;border:1px solid #e8d5c0;border-radius:16px;padding:28px;margin:36px 0;text-align:center;">
  <img src="{prod['image']}" alt="{keyword} — {prod['name']} | Divyaprabha Foods" style="max-width:250px;width:100%;height:auto;border-radius:12px;margin-bottom:16px;">
  <h3 style="color:#b01215;margin:8px 0 12px;font-size:22px;">{prod['name']}</h3>
  <p style="color:#3d1f0f;font-size:15px;line-height:1.6;margin-bottom:18px;">{prod['desc']}</p>
  <a href="/products/{prod['handle']}" style="background:#b01215;color:#fff;padding:14px 36px;border-radius:50px;font-weight:bold;text-decoration:none;display:inline-block;">Buy {keyword} Online →</a>
</div>
"""
            )
        elif i == 2:
            sections.append(
                f"<p>When you evaluate {keyword}, read the label for palm oil, glacial acetic acid, and sodium benzoate. "
                f"Heritage jars list mango, mustard oil, spices, and salt. Texture should stay firm; aroma should smell of "
                f"roasted seeds, not plastic tang. That checklist protects both flavour and trust.</p>"
            )
            sections.append(
                f"<p>Pair {keyword} with thepla, khichdi, bajra rotla, curd rice, or simple dal-bhaat. A teaspoon wakes "
                f"mild meals without drowning them. For gifting, glass jars travel better than open ceramic pots.</p>"
            )
            sections.append(
                f"<p>If you are building a pickle shelf, combine one sweet jar and one mustard-forward jar so weekday meals stay interesting. "
                f"Divyaprabha Foods designs <strong>{prod['name']}</strong> to sit in that rotation without flavour fatigue.</p>"
            )
        else:
            sections.append(
                f"<p>Store {keyword} sealed, away from sunlight, always with a dry spoon. Oil should remain above the fruit line; "
                f"top up with food-grade mustard oil if needed. Refrigeration after opening is optional in cool climates but "
                f"helps in humid monsoon kitchens.</p>"
            )
            sections.append(
                f"<p>Choosing Divyaprabha Foods means supporting a documented Saurashtra recipe rather than anonymous contract "
                f"manufacturing. Every CTA on this page points to a live product URL for <strong>{prod['name']}</strong> so you can "
                f"verify ingredients, jar photos, and availability before checkout.</p>"
            )
            sections.append(
                f"<p>Finally, remember that authentic {keyword} is seasonal craft bottled for year-round tables. When mango harvests shift, "
                f"honest makers adjust batch timing instead of forcing inferior fruit through the line. That discipline is why "
                f"repeat buyers return to the same brand after festivals and family visits.</p>"
            )

    # Closing depth block to secure 1200+ words
    sections.append(f"<h2>Why Divyaprabha Foods focuses on searchable {keyword} demand</h2>")
    sections.append(
        f"<p>Search phrases around {keyword} reveal real household intent: safer oil, homemade taste, Gujarati identity, and reliable delivery. "
        f"Content and collections on this store are built to answer those intents with product truth — not doorway pages. "
        f"When you click through to <a href=\"/products/{prod['handle']}\">{prod['name']}</a>, you are one step from the jar that matches this guide.</p>"
    )
    sections.append(
        f"<p>Use this article as a buying brief: confirm sun-curing language, mustard oil grade, mango style, and preservative stance. "
        f"Then compare aroma and crunch after your first spoonful. That loop — research, purchase, sensory check — is how Kathiyawadi families "
        f"have always judged achaar quality, whether the jar came from a neighbour’s terrace or a trusted online maker.</p>"
    )
    sections.append(
        f"<p>If you are comparing multiple brands of {keyword}, make a simple side-by-side notes table: oil type, sweetener (jaggery vs sugar), "
        f"fruit cut, chilli heat, and aftertaste at the 60-second mark. Divyaprabha Foods expects to win on oil cleanliness, fruit firmness, "
        f"and the absence of vinegar bite. Those notes also help you reorder the same sensory profile months later.</p>"
    )
    sections.append(
        f"<p>Share feedback with family elders who grew up with terrace-cured achar — their language (‘tikho’, ‘gor’, ‘khatto’) is still the best "
        f"quality rubric. When their verdict matches your jar of <strong>{prod['name']}</strong>, you know the {keyword} search led somewhere honest.</p>"
    )
    sections.append(
        f"<h2>Ingredient transparency checklist for {keyword}</h2>"
        f"<p>Before checkout, scan for: fruit identity (Rajapuri / keri style), oil (wood-pressed mustard vs palm), salt type, chilli variety, "
        f"and any mention of vinegar or benzoate. Divyaprabha Foods keeps the story short on purpose — fewer additives mean clearer flavour and "
        f"cleaner storage behaviour in humid Indian kitchens.</p>"
        f"<p>Also note packaging. Amber or clear food-grade glass protects aroma better than thin plastic. Labels should remain readable after "
        f"condensation. If a listing for {keyword} cannot show the jar from multiple angles, treat that as a trust gap.</p>"
        f"<p>Finally, plan usage: a 500g jar suits most nuclear families for weeks of daily thepla breakfasts, while 1kg suits joint families or "
        f"gifting. Match jar size to consumption so oil exposure cycles stay healthy and the last spoon still tastes vivid.</p>"
    )

    faq_html = ["<h2>Frequently asked questions about {}</h2>".format(keyword)]
    for q, a in faq:
        faq_html.append(f"<h3>{q}</h3><p>{a}</p>")

    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "author": {"@type": "Organization", "name": "Baa & The DivyaPrabha Culinary Team"},
        "publisher": {
            "@type": "Organization",
            "name": "Divyaprabha Foods",
            "logo": {
                "@type": "ImageObject",
                "url": "https://divyaprabhafoods.com/cdn/shop/files/logo.png",
            },
        },
        "datePublished": pub_date,
        "description": f"Buy authentic {keyword} online. Traditional Saurashtra homemade achar from Divyaprabha Foods.",
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq
        ],
    }

    html = "\n".join(
        [
            f'<script type="application/ld+json">{json.dumps(article_ld, ensure_ascii=False)}</script>',
            f'<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>',
            f'<p class="dp-lead">{leads[angle]}</p>',
            *sections,
            *faq_html,
        ]
    )
    excerpt = f"Authentic {keyword} guide — Saurashtra sun-cured homemade achar from Divyaprabha Foods."
    meta = {
        "title": title,
        "handle": handle,
        "tags": category,
        "product": prod,
        "angle": angle,
        "keyword": keyword,
        "pillar": pillar,
        "excerpt": excerpt[:150],
    }
    return title, handle, html, meta


def existing_article_handles() -> set[str]:
    handles = set()
    page_info = None
    # Shopify articles pagination via Link headers is complex; pull up to 250 repeatedly by since_id
    since_id = 0
    for _ in range(20):
        path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,handle,title,published_at"
        if since_id:
            path += f"&since_id={since_id}"
        data = api("GET", path)
        arts = data.get("articles") or []
        if not arts:
            break
        for a in arts:
            handles.add(a.get("handle") or "")
            since_id = max(since_id, a.get("id") or 0)
        if len(arts) < 250:
            break
        time.sleep(0.35)
    return handles


def random_daily_slots(start_day: dt.date, days: int, posts_per_day: int = 3) -> list[dt.datetime]:
    """Return unique random IST datetimes, posts_per_day per calendar day."""
    slots = []
    rng = random.Random(20260922)  # stable-ish across reruns for same start
    for d in range(days):
        day = start_day + dt.timedelta(days=d)
        # random minutes across morning/afternoon/evening windows
        windows = [(8, 11), (12, 16), (17, 21)]
        chosen = []
        for wi in range(posts_per_day):
            w = windows[wi % len(windows)]
            hour = rng.randint(w[0], w[1] - 1)
            minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            second = rng.choice([0, 12, 24, 36, 48])
            chosen.append(dt.datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=IST))
        # ensure unique & sorted
        chosen = sorted(set(chosen))
        while len(chosen) < posts_per_day:
            chosen.append(chosen[-1] + dt.timedelta(minutes=17))
            chosen = sorted(set(chosen))
        slots.extend(chosen[:posts_per_day])
    return slots


def keyword_jobs(registry) -> list[tuple[str, str | None]]:
    jobs = []
    for pillar, kws in (registry.get("pillars") or {}).items():
        for kw in kws:
            jobs.append((kw, pillar))
    for combo, kws in (registry.get("combos") or {}).items():
        for kw in kws:
            jobs.append((kw, combo))
    # Prefer global unique list order if present
    uniq = []
    seen = set()
    for kw, pillar in jobs:
        key = kw.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append((kw, pillar))
    return uniq


def create_scheduled_blogs(limit: int | None = None, start_offset_days: int = 1):
    """Legacy one-shot backlog fill (still no fixed calendar end when used with --ongoing)."""
    require_token()
    registry = load_registry()
    state = load_state()
    existing = existing_article_handles()
    existing |= set(state.get("blog_handles", {}).keys())

    jobs = keyword_jobs(registry)
    filtered = []
    for kw, p in jobs:
        h = slugify(f"{kw}-{pick_angle(kw)}")
        if h in existing:
            continue
        filtered.append((kw, p, h))

    if limit is not None:
        filtered = filtered[:limit]

    if not filtered:
        print("No unused first-pass keyword handles left — use --ongoing for continuous posting.")
        return

    days_needed = (len(filtered) + 2) // 3
    start_day = dt.datetime.now(IST).date() + dt.timedelta(days=start_offset_days)
    slots = random_daily_slots(start_day, days_needed, 3)
    _publish_blog_batch(filtered, slots, existing, state)


def latest_future_blog_date(existing_meta_handles: dict | None = None) -> dt.date | None:
    """Return the latest future published_at date already on Shopify/state, if any."""
    latest: dt.date | None = None
    now = dt.datetime.now(IST)
    # from API
    since_id = 0
    try:
        for _ in range(30):
            path = f"blogs/{BLOG_ID}/articles.json?limit=250&fields=id,published_at"
            if since_id:
                path += f"&since_id={since_id}"
            arts = api("GET", path).get("articles") or []
            if not arts:
                break
            for a in arts:
                raw = a.get("published_at") or ""
                if not raw:
                    continue
                try:
                    # Shopify returns UTC ISO
                    ts = dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(IST)
                except Exception:
                    continue
                if ts.date() >= now.date():
                    if latest is None or ts.date() > latest:
                        latest = ts.date()
                since_id = max(since_id, a.get("id") or 0)
            if len(arts) < 250:
                break
            time.sleep(0.25)
    except Exception as e:
        print(f"⚠️ Could not scan future blog dates: {e}")
    return latest


def create_ongoing_blogs(limit: int = 3, start_offset_days: int = 1):
    """Create `limit` blogs forever — appends after existing schedule (no end date)."""
    require_token()
    registry = load_registry()
    state = load_state()
    existing = existing_article_handles()
    existing |= set(state.get("blog_handles", {}).keys())
    jobs = keyword_jobs(registry)
    if not jobs:
        raise SystemExit("No keywords in arham_focus_keywords.json")

    angles = list(ANGLE_H2.keys())
    tomorrow = dt.datetime.now(IST).date() + dt.timedelta(days=start_offset_days)
    # Extend past any already-scheduled future posts so we never "end" the calendar
    latest = latest_future_blog_date()
    if latest and latest >= tomorrow:
        start_day = latest + dt.timedelta(days=1)
        print(f"Extending calendar after existing schedule ending {latest} → start {start_day}")
    else:
        start_day = tomorrow

    days_needed = max(1, (limit + 2) // 3)
    slots = random_daily_slots(start_day, days_needed, 3)[:limit]

    cursor = int(state.get("blog_cursor", 0))
    batch = []
    guard = 0
    while len(batch) < limit and guard < limit * 2000:
        guard += 1
        kw, pillar = jobs[cursor % len(jobs)]
        angle = angles[(cursor // len(jobs)) % len(angles)]
        slot = slots[len(batch)]
        suffix = slot.strftime("%Y%m%d") + f"-{cursor % 10000}"
        handle = slugify(f"{kw}-{angle}-{suffix}")
        cursor += 1
        if handle in existing:
            continue
        batch.append((kw, pillar, handle, angle, suffix, slot))

    state["blog_cursor"] = cursor
    save_state(state)

    print(
        f"Evergreen blogs: creating {len(batch)} (target {limit}/day) "
        f"from {start_day} — continuous, no end date."
    )
    created = 0
    for kw, pillar, handle, angle, suffix, slot in batch:
        pub_date = slot.date().isoformat()
        title, handle2, html, meta = build_article_html(
            kw, pillar, pub_date, angle=angle, handle_suffix=suffix
        )
        handle = handle2 or handle
        base = handle
        n = 2
        while handle in existing:
            handle = f"{base}-{n}"
            n += 1
        payload = {
            "article": {
                "title": title,
                "author": "Baa & The DivyaPrabha Culinary Team",
                "tags": meta["tags"],
                "body_html": html,
                "summary_html": meta["excerpt"],
                "handle": handle,
                "published": True,
                "published_at": slot.isoformat(),
                "image": {"src": meta["product"]["image"], "alt": f"{kw} — {meta['product']['name']}"},
            }
        }
        try:
            res = api("POST", f"blogs/{BLOG_ID}/articles.json", payload)
            art = res.get("article") or {}
            existing.add(handle)
            state.setdefault("blog_handles", {})[handle] = {
                "id": art.get("id"),
                "keyword": kw,
                "pillar": pillar,
                "published_at": slot.isoformat(),
                "title": title,
            }
            created += 1
            print(f"✅ [{created}/{len(batch)}] {slot.strftime('%Y-%m-%d %H:%M IST')} | {title}")
            save_state(state)
            time.sleep(0.45)
        except Exception as e:
            print(f"❌ Failed {kw}: {e}")
            time.sleep(1.0)
    print(f"\n🎉 Created/scheduled {created} evergreen articles (continues daily, no end date).")


def _publish_blog_batch(filtered, slots, existing, state):
    print(f"Creating {len(filtered)} blogs across slots from {slots[0].date() if slots else '?'}...")
    created = 0
    for idx, (kw, pillar, handle) in enumerate(filtered):
        slot = slots[idx]
        pub_date = slot.date().isoformat()
        title, handle, html, meta = build_article_html(kw, pillar, pub_date)
        base = handle
        n = 2
        while handle in existing:
            handle = f"{base}-{n}"
            n += 1
        payload = {
            "article": {
                "title": title,
                "author": "Baa & The DivyaPrabha Culinary Team",
                "tags": meta["tags"],
                "body_html": html,
                "summary_html": meta["excerpt"],
                "handle": handle,
                "published": True,
                "published_at": slot.isoformat(),
                "image": {"src": meta["product"]["image"], "alt": f"{kw} — {meta['product']['name']}"},
            }
        }
        try:
            res = api("POST", f"blogs/{BLOG_ID}/articles.json", payload)
            art = res.get("article") or {}
            existing.add(handle)
            state.setdefault("blog_handles", {})[handle] = {
                "id": art.get("id"),
                "keyword": kw,
                "pillar": pillar,
                "published_at": slot.isoformat(),
                "title": title,
            }
            created += 1
            print(f"✅ [{created}/{len(filtered)}] {slot.strftime('%Y-%m-%d %H:%M IST')} | {title}")
            save_state(state)
            time.sleep(0.45)
        except Exception as e:
            print(f"❌ Failed {kw}: {e}")
            time.sleep(1.0)
    print(f"\n🎉 Created/scheduled {created} articles.")


COLLECTION_SPECS = [
    ("special-mango-pickle", "Special Mango Pickle | Homemade Keri Achar", "Special Mango", "special_mango"),
    ("sweet-mango-pickle-gujarati", "Sweet Mango Pickle | Meethi Keri Achar", "Sweet Mango", "sweet_mango"),
    ("gor-keri-pickle-online", "Gor Keri Pickle Online | Jaggery Mango Achar", "Gor-Keri", "gor_keri"),
    ("chana-keri-methi-achar", "Chana Keri Methi Achar | Methia Pickle", "Chana Keri", "chana_keri"),
    ("gunda-keri-lasode-achar", "Gunda Keri Pickle | Lasode Ka Achar", "Gunda Keri", "gunda_keri"),
    ("aachar-masala-gujarati", "Aachar Masala | Gujarati Pickle Spice Mix Guide", "Aachar Masala", "chana_keri"),
    ("sweet-lemon-pickle-nimbu", "Sweet Lemon Pickle | Nimbu Achar Guide", "Sweet Lemon", "special_mango"),
    ("sweet-pickle-combo", "Sweet Pickle Combo | Gor Keri & Meethi Keri", "Sweet Combo", "gor_keri"),
    ("tangy-pickle-combo", "Tangy Pickle Combo | Gunda & Chana Keri", "Tangy Combo", "gunda_keri"),
    ("gujarati-pickle-6-combo", "Gujarati Pickle 6 Combo | Homemade Achar Packs", "6 Combo", "special_mango"),
]


def collection_body(title: str, pillar: str, prod_key: str, keywords: list[str]) -> str:
    prod = PRODUCTS[prod_key]
    top = ", ".join(keywords[:12]) if keywords else pillar
    return f"""
<h1>{title}</h1>
<p>Explore Divyaprabha Foods' focus on <strong>{pillar}</strong> — authentic Saurashtra homemade pickles built around searches like {top}. Every jar follows Baa's sun-curing tradition with wood-pressed yellow mustard oil and zero synthetic vinegar.</p>
<h2>Why shop {pillar} from Divyaprabha Foods?</h2>
<ul>
  <li>Small-batch Kathiyawadi recipes with transparent ingredients</li>
  <li>Solar moisture extraction for crunch that lasts 12+ months</li>
  <li>Live product CTA: <a href="/products/{prod['handle']}">{prod['name']}</a></li>
</ul>
<h2>Featured product</h2>
<p><img src="{prod['image']}" alt="{prod['name']}" style="max-width:280px;border-radius:12px;"></p>
<p>{prod['desc']}</p>
<p><a href="/products/{prod['handle']}">Buy {prod['name']} Online →</a></p>
<h2>Popular search themes in this collection</h2>
<p>{top}.</p>
"""


def existing_collection_handles() -> dict:
    existing = {}
    try:
        data = api("GET", "custom_collections.json?limit=250")
    except Exception as e:
        print(f"⚠️ Skipping collections — token lacks products/collections scope: {e}")
        return {}
    for c in data.get("custom_collections") or []:
        if c.get("handle"):
            existing[c["handle"]] = c
    return existing


def upsert_collections():
    require_token()
    registry = load_registry()
    state = load_state()
    pillars = registry.get("pillars") or {}
    combos = registry.get("combos") or {}
    existing = existing_collection_handles()
    if existing is None:
        return
    if not existing and TOKEN:
        # empty dict can mean API fail (already printed) or shop has zero — try create anyway if API worked
        pass

    for handle, title, pillar, prod_key in COLLECTION_SPECS:
        kws = pillars.get(pillar) or combos.get(pillar) or []
        body = collection_body(title, pillar, prod_key, kws)
        seo_title = clean_title(title)
        seo_desc = f"Buy authentic {pillar} style homemade Gujarati pickles online from Divyaprabha Foods. FSSAI crafted, sun-cured Saurashtra achar."[:160]
        if handle in existing:
            cid = existing[handle]["id"]
            api(
                "PUT",
                f"custom_collections/{cid}.json",
                {
                    "custom_collection": {
                        "id": cid,
                        "body_html": body,
                        "metafields_global_title_tag": seo_title,
                        "metafields_global_description_tag": seo_desc,
                    }
                },
            )
            print(f"🔄 Updated collection: {handle}")
        else:
            _create_collection(handle, title, body, seo_title, seo_desc, prod_key)
        state.setdefault("collection_handles", {})[handle] = {"pillar": pillar, "title": title}
        save_state(state)
        time.sleep(0.4)


def _create_collection(handle, title, body, seo_title, seo_desc, prod_key):
    res = api(
        "POST",
        "custom_collections.json",
        {
            "custom_collection": {
                "title": title,
                "handle": handle,
                "body_html": body,
                "published": True,
                "metafields_global_title_tag": seo_title,
                "metafields_global_description_tag": seo_desc,
            }
        },
    )
    cid = (res.get("custom_collection") or {}).get("id")
    print(f"✅ Created collection: {handle} (id={cid})")
    prod = PRODUCTS[prod_key]
    try:
        pdata = api("GET", f"products.json?handle={prod['handle']}")
        products = pdata.get("products") or []
        if products and cid:
            api(
                "POST",
                "collects.json",
                {"collect": {"collection_id": cid, "product_id": products[0]["id"]}},
            )
    except Exception as e:
        print(f"  (collect skip) {e}")
    return cid


def create_ongoing_collections(limit: int = 2):
    """Create up to `limit` NEW collection pages forever (weekly cadence = 2). No end date."""
    require_token()
    registry = load_registry()
    state = load_state()
    existing = existing_collection_handles()
    # If API 403, existing_collection_handles returns {} after print — detect via test call already done
    try:
        api("GET", "custom_collections.json?limit=1")
    except Exception as e:
        print(f"⚠️ Skipping collections — token lacks products/collections scope: {e}")
        return

    pillars = registry.get("pillars") or {}
    combos = registry.get("combos") or {}
    jobs = keyword_jobs(registry)
    if not jobs:
        raise SystemExit("No keywords for collections")

    # First finish static pillar specs, then evergreen keyword collections
    pending_specs = [
        (h, t, p, pk) for h, t, p, pk in COLLECTION_SPECS if h not in existing
    ]
    batch = []
    for h, t, p, pk in pending_specs:
        if len(batch) >= limit:
            break
        batch.append(("spec", h, t, p, pk))

    cursor = int(state.get("collection_cursor", 0))
    guard = 0
    while len(batch) < limit and guard < len(jobs) * 20:
        guard += 1
        kw, pillar = jobs[cursor % len(jobs)]
        cursor += 1
        prod_key = PILLAR_PRODUCT.get(pillar or "", "special_mango")
        if pillar and pillar in PILLAR_PRODUCT:
            prod_key = PILLAR_PRODUCT[pillar]
        else:
            # infer from keyword via map_product reverse
            prod = map_product(pillar, kw)
            prod_key = next(k for k, v in PRODUCTS.items() if v["handle"] == prod["handle"])
        handle = slugify(f"{kw}-homemade-achar")
        if handle in existing or any(b[1] == handle for b in batch):
            handle = slugify(f"{kw}-buy-online")
        if handle in existing or any(b[1] == handle for b in batch):
            handle = slugify(f"{kw}-collection-{cursor}")
        if handle in existing or any(b[1] == handle for b in batch):
            continue
        title = clean_title(f"{kw} | Homemade Achar Collection")
        batch.append(("kw", handle, title, pillar or kw, prod_key, kw))

    state["collection_cursor"] = cursor
    save_state(state)

    print(
        f"Evergreen collections: creating {len(batch)} this week "
        f"(limit={limit}/week, no end date)."
    )
    for item in batch:
        if item[0] == "spec":
            _, handle, title, pillar, prod_key = item
            kws = pillars.get(pillar) or combos.get(pillar) or [pillar]
            seed_kw = pillar
        else:
            _, handle, title, pillar, prod_key, seed_kw = item
            kws = [seed_kw] + (pillars.get(pillar) or combos.get(pillar) or [])[:10]
        body = collection_body(title, pillar, prod_key, kws)
        seo_title = clean_title(title)
        seo_desc = f"Buy authentic {seed_kw if item[0]=='kw' else pillar} homemade Gujarati pickles online from Divyaprabha Foods."[:160]
        try:
            cid = _create_collection(handle, title, body, seo_title, seo_desc, prod_key)
            existing[handle] = {"id": cid}
            state.setdefault("collection_handles", {})[handle] = {
                "pillar": pillar,
                "title": title,
                "id": cid,
            }
            save_state(state)
        except Exception as e:
            print(f"❌ collection {handle}: {e}")
        time.sleep(0.4)
    print(f"Done. Created {len(batch)} collections; continues weekly with no end date.")


def status():
    registry = load_registry()
    jobs = keyword_jobs(registry)
    state = load_state()
    print("Keywords unique jobs:", len(jobs))
    print("Blogs recorded in state:", len(state.get("blog_handles") or {}))
    print("Collections recorded:", len(state.get("collection_handles") or {}))
    print("Cadence: 3 blogs/day + 2 collections/week — continuous, no end date")
    if TOKEN:
        try:
            api("GET", f"blogs/{BLOG_ID}/articles.json?limit=1&published_status=any")
            print("API reachable: yes")
        except Exception as e:
            print("API reachable: no ->", e)
    else:
        print("TOKEN: missing")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--collections", action="store_true")
    parser.add_argument("--blogs", action="store_true")
    parser.add_argument(
        "--ongoing",
        action="store_true",
        help="Continuous mode: no backlog end date (default for scheduled runs)",
    )
    parser.add_argument("--all", action="store_true", help="Process full remaining first-pass blog backlog")
    parser.add_argument("--limit", type=int, default=3, help="Blog batch size (ongoing default = 3/day)")
    parser.add_argument("--collection-limit", type=int, default=2, help="New collections per run (default 2/week)")
    parser.add_argument("--start-offset-days", type=int, default=1)
    args = parser.parse_args()

    if args.status or (not args.collections and not args.blogs):
        status()
    if args.collections:
        if args.ongoing:
            create_ongoing_collections(args.collection_limit)
        else:
            upsert_collections()
    if args.blogs:
        if args.all and not args.ongoing:
            create_scheduled_blogs(limit=None, start_offset_days=args.start_offset_days)
        else:
            create_ongoing_blogs(limit=args.limit, start_offset_days=args.start_offset_days)


if __name__ == "__main__":
    main()
