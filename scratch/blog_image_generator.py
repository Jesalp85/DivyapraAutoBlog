#!/usr/bin/env python3
"""
Divyaprabha Foods — unique featured image for every new blog post.

The product itself is NEVER generated or redrawn by AI:
  1. AI generates only an empty, brand-coloured background scene (varies per blog:
     keyword, angle, product props, lighting, surface).
  2. The real jar is a cutout of the store's own product photo
     (scratch/product_cutouts/<product-handle>.png) and is pasted on top pixel-for-pixel,
     so jar colour, shape, label, cloth lid and packaging stay exactly as sold.
  3. If no AI key / cutout is available, the original CDN product photo is used instead.

Env (first provider with a key wins):
  CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID  (Workers AI, model CLOUDFLARE_IMAGE_MODEL, default @cf/black-forest-labs/flux-1-schnell)
  GEMINI_API_KEY  (model GEMINI_IMAGE_MODEL, default gemini-2.5-flash-image)
  OPENAI_API_KEY  (model OPENAI_IMAGE_MODEL, default gpt-image-1)
  BLOG_IMAGE_PROVIDER=cloudflare|gemini|openai   optional, forces provider order

Usage:
  # one-time / whenever a product photo changes (needs: pip install "rembg[cpu]" pillow)
  python3 scratch/blog_image_generator.py --build-cutouts

  # local preview of what a blog image will look like
  python3 scratch/blog_image_generator.py --preview "Mango Aachar" --angle buy \
      --product mango-pickle-traditional-keri-achar-gujarati --out /tmp/preview.jpg
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUTOUT_DIR = ROOT / "scratch" / "product_cutouts"
MANIFEST_PATH = CUTOUT_DIR / "manifest.json"
CTX = ssl.create_default_context()

CANVAS = (1600, 1000)  # 16:10 = blog card ratio; jar kept inside the 2.7:1 article-hero crop band
JAR_TOP, JAR_BOTTOM = 0.23, 0.79
JAR_MAX_WIDTH = 0.52

BRAND_PALETTE = (
    "warm cream (#fdf6ed), sandy beige (#e8d5c0), deep maroon red (#b01215) accents "
    "and earthy dark-brown wood (#3d1f0f)"
)

# Keyed by live product handle. `accent` mirrors the colour wash on each product's own photo.
PRODUCT_STYLE = {
    "mango-pickle-traditional-keri-achar-gujarati": {
        "accent": "soft sage green",
        "props": "whole green Rajapuri raw mangoes, halved mango pieces, a small brass bowl of yellow mustard seeds, dried red chillies",
    },
    "sweet-mango-pickle-meethi-keri-achar-homemade": {
        "accent": "golden mango yellow",
        "props": "ripe-green mango slices, chunks of golden jaggery, cinnamon sticks, a few cloves",
    },
    "gor-keri-pickle-jaggery-mango-achar-gujarati": {
        "accent": "warm terracotta peach",
        "props": "blocks of organic jaggery (gur), Kashmiri red chillies, raw mango wedges, fennel seeds",
    },
    "chana-keri-methi-pickle-gujarati-methia-achar": {
        "accent": "turmeric ochre",
        "props": "small heaps of chickpeas (kala chana), fenugreek seeds, turmeric root, raw mango cubes",
    },
    "gunda-keri-pickle-lasode-ka-achar-gujarati": {
        "accent": "fresh lime green",
        "props": "fresh green gunda berries (lasoda / glueberries), grated raw mango, split mustard seeds",
    },
    "chhundo-pickle-sweet-shredded-mango-achar-gujarati": {
        "accent": "dusty rose mauve",
        "props": "finely grated raw mango on a steel plate, jaggery pieces, red chilli powder in a small katori",
    },
    "katka-keri-pickle-homemade-gujarati-mango-achar": {
        "accent": "chilli red",
        "props": "crunchy raw mango cubes, a copper ladle of mustard oil, dried red chillies, turmeric powder",
    },
}

ANGLE_SCENES = {
    "heritage": [
        "a sunlit Saurashtra village courtyard with a whitewashed wall, clay matka pots and a charpai in the soft background",
        "a traditional Kathiyawadi rooftop in summer with salted mango pieces drying on cotton cloth in the background",
        "an old Gujarati home kitchen with brass utensils on wooden shelves, softly out of focus",
    ],
    "health": [
        "a bright, airy Indian kitchen counter with fresh turmeric, whole spices and a small bottle-free bowl of golden mustard oil at the edges",
        "a clean stone slab surrounded by raw spices — mustard seeds, fenugreek, turmeric, rock salt (sendha namak) — arranged neatly at the sides",
        "a morning window-lit kitchen with green herbs and whole spices in small brass katoris at the edges",
    ],
    "buy": [
        "a warm, premium pantry shelf setting with woven jute cloth and soft bokeh lights",
        "an elegant gifting table with a jute runner, marigold flowers and a folded handloom cloth at the sides",
        "a cosy modern Indian dining table with a handloom cloth and soft afternoon light",
    ],
    "pairing": [
        "a Gujarati breakfast spread at the edges — methi thepla, a bowl of dahi, masala chai in a steel cup",
        "a traditional Kathiyawadi thali at the sides — bajra rotla, dal, rice and white butter",
        "a travel tiffin scene with steel dabbas, khakhra and paratha at the edges",
    ],
    "craft": [
        "a rustic workspace with a wooden chopping board, sliced raw mango and a hand-pounded stone mortar at the edges",
        "a ceramic martban and a sun-dried cotton cloth in the soft background of a traditional workshop",
        "hands-free close-up of spice grinding tools — silbatta stone and brass bowls — at the edges of a wooden table",
    ],
}

LIGHTS = [
    "golden-hour sunlight from the left with long soft shadows",
    "soft diffused morning daylight",
    "warm late-afternoon window light",
    "bright natural midday light with gentle shadows",
]

SURFACES = [
    "a dark-brown sheesham wood table",
    "a weathered light wooden plank table",
    "a cream kota stone slab",
    "a maroon handloom cloth over a wooden table",
]


def _seed(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode("utf-8")).hexdigest(), 16)


def build_prompt(keyword: str, angle: str, product_handle: str, blog_handle: str) -> str:
    style = PRODUCT_STYLE.get(product_handle) or PRODUCT_STYLE["mango-pickle-traditional-keri-achar-gujarati"]
    seed = _seed(blog_handle or keyword, angle)
    scenes = ANGLE_SCENES.get(angle) or ANGLE_SCENES["heritage"]
    scene = scenes[seed % len(scenes)]
    light = LIGHTS[(seed // 7) % len(LIGHTS)]
    surface = SURFACES[(seed // 31) % len(SURFACES)]
    return (
        "Photorealistic premium editorial food-photography BACKGROUND for an artisanal Gujarati pickle brand, "
        f"for a blog article about '{keyword}'. "
        f"Setting: {scene}. Foreground surface: {surface}. "
        f"Props placed only near the left and right edges: {style['props']}. "
        f"Colour palette: {BRAND_PALETTE}, with a subtle hint of {style['accent']}. "
        f"Lighting: {light}. Wide 16:10 landscape frame, shallow depth of field. "
        "Camera: straight-on side view at table height (like a product shot), NOT top-down, NOT flat lay, NOT overhead — "
        "the table top fills the lower half and a softly blurred back wall or background scene fills the upper half. "
        "IMPORTANT: the centre of the table must be a clean, empty surface — keep the middle 45% of the image "
        "completely free of objects, because a product will be placed there later. "
        "Absolutely no jars, bottles, containers, packaging, text, letters, logos, labels, watermarks or people."
    )


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{url.split('?')[0]} -> {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}") from e


def _gemini_background(prompt: str, key: str) -> bytes:
    model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
    headers = {"x-goog-api-key": key}
    if model.startswith("imagen"):
        res = _post_json(
            f"{base}:predict",
            {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}},
            headers,
        )
        return base64.b64decode(res["predictions"][0]["bytesBase64Encoded"])
    res = _post_json(
        f"{base}:generateContent",
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}},
        },
        headers,
    )
    for cand in res.get("candidates") or []:
        for part in (cand.get("content") or {}).get("parts") or []:
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return base64.b64decode(data)
    raise RuntimeError(f"Gemini returned no image: {json.dumps(res)[:300]}")


def _cloudflare_background(prompt: str, token: str) -> bytes:
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not account:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID not set")
    # flux-1-schnell ≈ 100 images/day on the 10k-neuron free tier; lucid-origin at 1536x960 ≈ 4/day.
    model = os.environ.get("CLOUDFLARE_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
    payload = {"prompt": prompt}
    if "flux-1-schnell" in model:
        payload["steps"] = 8
    else:
        payload.update({"width": 1536, "height": 960})
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=180) as resp:
            body = resp.read()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Cloudflare {model} -> {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}") from e
    if ctype.startswith("image/"):
        return body
    image = (json.loads(body).get("result") or {}).get("image")
    if not image:
        raise RuntimeError(f"Cloudflare {model} returned no image: {body[:300]!r}")
    return base64.b64decode(image)


def _openai_background(prompt: str, key: str) -> bytes:
    res = _post_json(
        "https://api.openai.com/v1/images/generations",
        {
            "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            "prompt": prompt,
            "size": "1536x1024",
            "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "medium"),
            "n": 1,
        },
        {"Authorization": f"Bearer {key}"},
    )
    return base64.b64decode(res["data"][0]["b64_json"])


def generate_background(prompt: str) -> bytes | None:
    providers = {
        "cloudflare": (os.environ.get("CLOUDFLARE_API_TOKEN", "").strip(), _cloudflare_background),
        "gemini": (os.environ.get("GEMINI_API_KEY", "").strip(), _gemini_background),
        "openai": (os.environ.get("OPENAI_API_KEY", "").strip(), _openai_background),
    }
    order = ["cloudflare", "gemini", "openai"]
    forced = os.environ.get("BLOG_IMAGE_PROVIDER", "").strip().lower()
    if forced in providers:
        order.remove(forced)
        order.insert(0, forced)
    for name in order:
        key, fn = providers[name]
        if not key:
            continue
        try:
            return fn(prompt, key)
        except Exception as e:
            print(f"   ⚠️ {name} background failed: {e}")
    return None


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
        return resp.read()


def _drop_stray_fragments(cut, min_share: float = 0.02):
    """Remove leftover bits of the photo's sketched backdrop (islands far smaller than the jar/bowl)."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage

    rgba = np.array(cut)
    solid = rgba[..., 3] > 16
    # Opening detaches thin sketch lines that touch the jar edge; the jar, lid rope and bowl survive it.
    labels, count = ndimage.label(ndimage.binary_opening(solid, iterations=3))
    if count == 0:
        return cut
    sizes = ndimage.sum(np.ones_like(labels), labels, index=range(1, count + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * min_share]
    region = ndimage.binary_dilation(np.isin(labels, keep), iterations=4) & solid
    rgba[..., 3] = np.where(region, rgba[..., 3], 0)
    return Image.fromarray(rgba)


def build_cutout(product_handle: str, image_url: str):
    """Cut the real jar (and its serving bowl) out of the store product photo."""
    from PIL import Image
    from rembg import new_session, remove

    model = os.environ.get("REMBG_MODEL", "isnet-general-use")
    src = Image.open(io.BytesIO(_download(image_url))).convert("RGB")
    cut = remove(src, session=new_session(model), post_process_mask=True)
    cut = _drop_stray_fragments(cut)
    cut = cut.crop(cut.getbbox())
    CUTOUT_DIR.mkdir(parents=True, exist_ok=True)
    cut.save(CUTOUT_DIR / f"{product_handle}.png", optimize=True)
    manifest = _load_manifest()
    manifest[product_handle] = image_url
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return cut


def load_cutout(product_handle: str, image_url: str):
    """Return the cutout only if it was made from the product's CURRENT photo (packaging never goes stale)."""
    from PIL import Image

    path = CUTOUT_DIR / f"{product_handle}.png"
    if path.exists() and _load_manifest().get(product_handle) == image_url:
        return Image.open(path).convert("RGBA")
    try:
        return build_cutout(product_handle, image_url)
    except ImportError:
        print(f"   ⚠️ Cutout for {product_handle} missing/stale and rembg not installed.")
    except Exception as e:
        print(f"   ⚠️ Cutout for {product_handle} failed: {e}")
    return None


def compose(background_bytes: bytes, cutout) -> bytes:
    from PIL import Image, ImageFilter, ImageOps

    w, h = CANVAS
    bg = ImageOps.fit(Image.open(io.BytesIO(background_bytes)).convert("RGB"), CANVAS, Image.LANCZOS)
    # Pull the AI scene toward the brand cream so every post sits in the same theme (background only).
    bg = Image.blend(bg, Image.new("RGB", CANVAS, (253, 246, 237)), 0.08)

    target_h = int(h * (JAR_BOTTOM - JAR_TOP))
    scale = min(target_h / cutout.height, (w * JAR_MAX_WIDTH) / cutout.width)
    jar = cutout.resize((int(cutout.width * scale), int(cutout.height * scale)), Image.LANCZOS)
    x = (w - jar.width) // 2
    y = int(h * JAR_BOTTOM) - jar.height

    alpha = jar.split()[-1]
    shadow = Image.new("L", CANVAS, 0)
    shadow.paste(alpha.point(lambda a: int(a * 0.45)), (x + 18, y + 22))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    contact = Image.new("L", CANVAS, 0)
    band = Image.new("L", (int(jar.width * 0.9), max(24, jar.height // 14)), 150)
    contact.paste(band, (x + int(jar.width * 0.05), y + jar.height - band.height // 2))
    contact = contact.filter(ImageFilter.GaussianBlur(22))
    dark = Image.new("RGB", CANVAS, (61, 31, 15))
    bg = Image.composite(dark, bg, shadow)
    bg = Image.composite(dark, bg, contact)

    bg.paste(jar, (x, y), jar)
    out = io.BytesIO()
    bg.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out.getvalue()


def featured_image(
    keyword: str,
    angle: str,
    product_handle: str,
    product_image_url: str,
    blog_handle: str,
    alt: str,
) -> dict:
    """Shopify `article.image` payload: unique composited image, or the real CDN photo as fallback."""
    fallback = {"src": product_image_url, "alt": alt}
    try:
        cutout = load_cutout(product_handle, product_image_url)
        if cutout is None:
            return fallback
        background = generate_background(build_prompt(keyword, angle, product_handle, blog_handle))
        if background is None:
            print("   ⚠️ No AI background (set GEMINI_API_KEY or OPENAI_API_KEY) — using product photo.")
            return fallback
        jpg = compose(background, cutout)
    except Exception as e:
        print(f"   ⚠️ Featured image generation failed, using product photo: {e}")
        return fallback
    print(f"   🖼  Generated unique featured image ({len(jpg) // 1024} KB)")
    return {
        "attachment": base64.b64encode(jpg).decode("ascii"),
        "filename": f"{blog_handle}.jpg",
        "alt": alt,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-cutouts", action="store_true", help="(Re)build jar cutouts for all live products")
    parser.add_argument("--preview", metavar="KEYWORD")
    parser.add_argument("--angle", default="heritage", choices=sorted(ANGLE_SCENES))
    parser.add_argument("--product", default="mango-pickle-traditional-keri-achar-gujarati")
    parser.add_argument("--handle", default="", help="Blog handle (drives scene variation)")
    parser.add_argument("--out", default="/tmp/dp-blog-preview.jpg")
    args = parser.parse_args()

    if args.build_cutouts:
        import arham_keyword_content_engine as engine

        for prod in engine.PRODUCTS.values():
            build_cutout(prod["handle"], prod["image"])
            print(f"✅ cutout: {prod['handle']}")

    if args.preview:
        import arham_keyword_content_engine as engine

        prod = next(p for p in engine.PRODUCTS.values() if p["handle"] == args.product)
        handle = args.handle or f"{args.preview}-{args.angle}".lower().replace(" ", "-")
        prompt = build_prompt(args.preview, args.angle, prod["handle"], handle)
        print(prompt)
        cutout = load_cutout(prod["handle"], prod["image"])
        background = generate_background(prompt)
        if cutout is None or background is None:
            raise SystemExit("❌ Need a cutout and an AI key (GEMINI_API_KEY / OPENAI_API_KEY) to preview.")
        Path(args.out).write_bytes(compose(background, cutout))
        print(f"✅ Preview saved: {args.out}")


if __name__ == "__main__":
    main()
