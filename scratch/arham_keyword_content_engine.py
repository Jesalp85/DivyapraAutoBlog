#!/usr/bin/env python3
"""
Divyaprabha Foods — Arham keyword blog + collection engine

- Reads scratch/arham_focus_keywords.json (from Excel)
- Creates unique SEO blog articles (1200+ words HTML) mapped to live products
- Schedules 3 posts/day at RANDOM IST times
- Creates/updates SEO collection pages for product pillars + combos
- Continues until keyword backlog is exhausted (re-run safely; skips existing handles)

Usage:
  export SHOPIFY_ACCESS_TOKEN=shpat_xxx
  python3 scratch/arham_keyword_content_engine.py --status
  python3 scratch/arham_keyword_content_engine.py --collections
  python3 scratch/arham_keyword_content_engine.py --blogs --limit 30
  python3 scratch/arham_keyword_content_engine.py --blogs --all
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


def pick_angle(keyword: str) -> str:
    h = int(hashlib.md5(keyword.lower().encode()).hexdigest(), 16)
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


def build_article_html(keyword: str, pillar: str | None, pub_date: str) -> tuple[str, str, str, dict]:
    prod = map_product(pillar, keyword)
    angle = pick_angle(keyword)
    h2s = [h.format(kw=keyword) for h in ANGLE_H2[angle]]
    title = clean_title(f"{keyword}: Gujarati Homemade Achar Guide")
    if len(title) > 59:
        title = clean_title(f"{keyword} Homemade Achar")
    category = CATEGORIES[int(hashlib.md5(keyword.encode()).hexdigest(), 16) % len(CATEGORIES)]
    handle = slugify(f"{keyword}-{angle}")

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
    require_token()
    registry = load_registry()
    state = load_state()
    existing = existing_article_handles()
    existing |= set(state.get("blog_handles", {}).keys())

    jobs = keyword_jobs(registry)
    pending = [(kw, p) for kw, p in jobs if slugify(f"{kw}-{pick_angle(kw)}") not in existing]
    # also skip if any handle collision with simpler slug
    filtered = []
    for kw, p in pending:
        h = slugify(f"{kw}-{pick_angle(kw)}")
        if h in existing:
            continue
        filtered.append((kw, p, h))

    if limit is not None:
        filtered = filtered[:limit]

    if not filtered:
        print("✅ No pending keyword blogs — backlog complete or already created.")
        return

    days_needed = (len(filtered) + 2) // 3
    start_day = dt.datetime.now(IST).date() + dt.timedelta(days=start_offset_days)
    slots = random_daily_slots(start_day, days_needed, 3)

    print(f"Creating {len(filtered)} blogs across ~{days_needed} days from {start_day} (3/day, random IST times)...")
    created = 0
    for idx, (kw, pillar, handle) in enumerate(filtered):
        slot = slots[idx]
        pub_date = slot.date().isoformat()
        title, handle, html, meta = build_article_html(kw, pillar, pub_date)
        # ensure unique handle
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


def upsert_collections():
    require_token()
    registry = load_registry()
    state = load_state()
    pillars = registry.get("pillars") or {}
    combos = registry.get("combos") or {}

    # existing custom collections
    existing = {}
    data = api("GET", "custom_collections.json?limit=250")
    for c in data.get("custom_collections") or []:
        existing[c.get("handle")] = c

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
            # collect products into collection
            prod = PRODUCTS[prod_key]
            # find product id
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
        state.setdefault("collection_handles", {})[handle] = {"pillar": pillar, "title": title}
        save_state(state)
        time.sleep(0.4)


def status():
    registry = load_registry()
    jobs = keyword_jobs(registry)
    state = load_state()
    print("Keywords unique jobs:", len(jobs))
    print("Blogs recorded in state:", len(state.get("blog_handles") or {}))
    print("Collections recorded:", len(state.get("collection_handles") or {}))
    if TOKEN:
        try:
            arts = api("GET", f"blogs/{BLOG_ID}/articles.json?limit=1&published_status=unpublished")
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
    parser.add_argument("--all", action="store_true", help="Process full remaining blog backlog")
    parser.add_argument("--limit", type=int, default=21, help="Blog batch size (default 21 = 7 days)")
    parser.add_argument("--start-offset-days", type=int, default=1)
    args = parser.parse_args()

    if args.status or (not args.collections and not args.blogs):
        status()
    if args.collections:
        upsert_collections()
    if args.blogs:
        lim = None if args.all else args.limit
        create_scheduled_blogs(limit=lim, start_offset_days=args.start_offset_days)


if __name__ == "__main__":
    main()
