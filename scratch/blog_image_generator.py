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
        "a sunlit Saurashtra village courtyard, whitewashed lime-plaster wall, terracotta matka pots and a woven charpai softly blurred behind",
        "a Kathiyawadi terrace at golden hour, salted raw mango pieces drying on white muslin cloth in the blurred background",
        "a heritage Gujarati kitchen with gleaming brass and copper vessels on carved wooden shelves, beautifully out of focus",
    ],
    "health": [
        "a bright, airy Indian kitchen with a window, fresh turmeric roots, curry leaves and whole spices styled in small brass katoris",
        "a pale stone counter with neat little heaps of mustard seeds, fenugreek, turmeric powder and pink rock salt",
        "a fresh morning kitchen with green herbs, a copper pot and sunlight falling through a jaali window",
    ],
    "buy": [
        "a premium festive gifting table with a jute runner, marigold garlands, diya lamps and warm golden bokeh lights",
        "an elegant boutique pantry shelf with woven baskets and warm bokeh, luxurious and inviting",
        "a cosy modern Indian dining table with a handloom runner, fresh flowers and soft afternoon light",
    ],
    "pairing": [
        "a styled Gujarati breakfast: methi thepla stacked on a brass plate, a bowl of dahi and masala chai in a steel cup",
        "a Kathiyawadi thali setting with bajra rotla, dal, jeera rice and a dollop of white butter on brass plates",
        "a travel tiffin moment with steel dabbas, khakhra and parathas wrapped in cloth",
    ],
    "craft": [
        "a rustic artisan kitchen with a wooden chopping board, freshly cut raw mango and a stone mortar and pestle",
        "a traditional pickling room with ceramic martbans and sun-bleached cotton cloth, softly blurred",
        "a silbatta grinding stone, brass bowls of whole spices and scattered mustard seeds on an old wooden table",
    ],
}

# (lighting description, shadow direction: +1 shadow falls right, -1 falls left)
LIGHTS = [
    ("warm golden-hour sunlight streaming in from the left, visible soft sunbeams and long gentle shadows", 1),
    ("soft morning window light from the right, airy and fresh", -1),
    ("warm late-afternoon sunlight from the left with dappled leaf shadows", 1),
    ("glowing sunlight from the right with a gentle warm haze", -1),
]

SURFACES = [
    "a rich dark-brown sheesham wood table with visible grain",
    "a weathered honey-toned wooden plank table",
    "a cream kota stone slab",
    "a deep maroon handloom cloth over a wooden table",
]


def _seed(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode("utf-8")).hexdigest(), 16)


def scene_plan(keyword: str, angle: str, product_handle: str, blog_handle: str) -> dict:
    """Prompt for the background plus the light direction the composited jar's shadow must follow."""
    style = PRODUCT_STYLE.get(product_handle) or PRODUCT_STYLE["mango-pickle-traditional-keri-achar-gujarati"]
    seed = _seed(blog_handle or keyword, angle)
    scenes = ANGLE_SCENES.get(angle) or ANGLE_SCENES["heritage"]
    scene = scenes[seed % len(scenes)]
    light, shadow_dir = LIGHTS[(seed // 7) % len(LIGHTS)]
    surface = SURFACES[(seed // 31) % len(SURFACES)]
    prompt = (
        "Award-winning commercial food advertising photograph, ultra realistic, magazine cover quality, "
        "shot on a Canon EOS R5 with an 85mm lens at f/2.8, rich natural textures, appetising and inviting. "
        f"Scene for an artisanal Gujarati pickle brand ('{keyword}'): {scene}. "
        f"In the foreground, {surface} seen straight-on from table height, filling the lower half of the frame; "
        "the background scene is creamy and softly blurred with beautiful bokeh. "
        f"Styled props only at the far left and far right edges: {style['props']}. "
        f"Lighting: {light}. "
        f"Colour palette: {BRAND_PALETTE}, with a subtle hint of {style['accent']}; warm, premium and harmonious. "
        "The centre of the table is completely clear and empty, an open hero spot waiting for a product. "
        "No jars, no bottles, no packaging, no text, no logos, no people."
    )
    return {"prompt": prompt, "shadow_dir": shadow_dir}


def build_prompt(keyword: str, angle: str, product_handle: str, blog_handle: str) -> str:
    return scene_plan(keyword, angle, product_handle, blog_handle)["prompt"]


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


def _fit_background(background_bytes: bytes):
    from PIL import Image, ImageOps

    return ImageOps.fit(Image.open(io.BytesIO(background_bytes)).convert("RGB"), CANVAS, Image.LANCZOS)


def centre_clutter(background_bytes: bytes) -> float:
    """Edge density where the jar will stand — lower means a cleaner hero spot."""
    from PIL import ImageFilter, ImageStat

    w, h = CANVAS
    grey = _fit_background(background_bytes).convert("L")
    box = grey.crop((int(w * 0.28), int(h * JAR_TOP), int(w * 0.72), int(h * JAR_BOTTOM)))
    return ImageStat.Stat(box.filter(ImageFilter.FIND_EDGES)).mean[0]


def _radial_mask(size, centre, radii, inner: int, outer: int):
    """Elliptical gradient: `inner` value at the centre fading to `outer` at the radii."""
    from PIL import Image

    w, h = size
    small = Image.new("L", (w // 8, h // 8))
    cx, cy = centre[0] / 8, centre[1] / 8
    rx, ry = radii[0] / 8, radii[1] / 8
    px = small.load()
    for yy in range(small.height):
        for xx in range(small.width):
            d = min(1.0, (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) ** 0.5)
            px[xx, yy] = int(inner + (outer - inner) * d)
    return small.resize(size, Image.BILINEAR)


def compose(background_bytes: bytes, cutout, shadow_dir: int = 1) -> bytes:
    """Real jar on the AI scene. Every grading step touches the background only; jar pixels are pasted as-is."""
    import numpy as np
    from PIL import Image, ImageChops, ImageFilter

    w, h = CANVAS
    bg = _fit_background(background_bytes)
    bg = Image.blend(bg, Image.new("RGB", CANVAS, (253, 246, 237)), 0.06)

    # Shallow depth of field: soften the upper backdrop, keep the table near the jar crisp.
    fade = Image.linear_gradient("L").resize(CANVAS).point(lambda v: max(0, 255 - int(v * 1.9)))
    bg = Image.composite(bg.filter(ImageFilter.GaussianBlur(3)), bg, fade)

    target_h = int(h * (JAR_BOTTOM - JAR_TOP))
    scale = min(target_h / cutout.height, (w * JAR_MAX_WIDTH) / cutout.width)
    jar = cutout.resize((int(cutout.width * scale), int(cutout.height * scale)), Image.LANCZOS)
    x = (w - jar.width) // 2
    y = int(h * JAR_BOTTOM) - jar.height

    # Warm glow behind the product so it pops, plus a gentle vignette to lead the eye to the centre.
    glow = _radial_mask(CANVAS, (w // 2, y + jar.height * 0.45), (jar.width * 1.1, jar.height * 0.9), 70, 0)
    bg = Image.composite(ImageChops.screen(bg, Image.new("RGB", CANVAS, (255, 226, 180))), bg, glow)
    vignette = _radial_mask(CANVAS, (w // 2, h // 2), (w * 0.75, h * 0.8), 0, 90)
    bg = Image.composite(Image.new("RGB", CANVAS, (40, 20, 10)), bg, vignette)

    alpha = jar.split()[-1]
    dark = Image.new("RGB", CANVAS, (35, 18, 8))

    # Soft cast shadow falling away from the scene's light source.
    cast = Image.new("L", CANVAS, 0)
    cast.paste(alpha.point(lambda a: int(a * 0.32)), (x + shadow_dir * int(jar.width * 0.07), y + 16))
    bg = Image.composite(dark, bg, cast.filter(ImageFilter.GaussianBlur(30)))

    # Contact shadows traced along each column's lowest opaque pixel, so jar and bowl each touch the table.
    solid = np.array(alpha) > 128
    bottoms = solid.shape[0] - 1 - np.argmax(solid[::-1], axis=0)
    columns = np.where(solid.any(axis=0))[0]
    for above, below, opacity, blur, drift in ((10, 26, 0.4, 14, 0.05), (3, 7, 0.75, 4, 0.0)):
        mask = np.zeros((jar.height + below + 4, jar.width), dtype=np.uint8)
        for c in columns:
            b = bottoms[c]
            mask[max(0, b - above): b + below, c] = int(255 * opacity)
        layer = Image.new("L", CANVAS, 0)
        layer.paste(Image.fromarray(mask), (x + shadow_dir * int(jar.width * drift), y))
        bg = Image.composite(dark, bg, layer.filter(ImageFilter.GaussianBlur(blur)))

    bg.paste(jar, (x, y), jar)
    out = io.BytesIO()
    bg.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return out.getvalue()


def best_background(prompt: str) -> bytes | None:
    """Generate a few candidates and keep the one with the emptiest, cleanest centre."""
    candidates = []
    for _ in range(max(1, int(os.environ.get("BLOG_IMAGE_CANDIDATES", "2")))):
        img = generate_background(prompt)
        if img is None:
            break
        candidates.append(img)
    if not candidates:
        return None
    return min(candidates, key=centre_clutter)


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
        plan = scene_plan(keyword, angle, product_handle, blog_handle)
        background = best_background(plan["prompt"])
        if background is None:
            print("   ⚠️ No AI background (set CLOUDFLARE_API_TOKEN, GEMINI_API_KEY or OPENAI_API_KEY) — using product photo.")
            return fallback
        jpg = compose(background, cutout, plan["shadow_dir"])
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
        plan = scene_plan(args.preview, args.angle, prod["handle"], handle)
        print(plan["prompt"])
        cutout = load_cutout(prod["handle"], prod["image"])
        background = best_background(plan["prompt"])
        if cutout is None or background is None:
            raise SystemExit("❌ Need a cutout and an AI key (CLOUDFLARE_API_TOKEN / GEMINI_API_KEY / OPENAI_API_KEY).")
        Path(args.out).write_bytes(compose(background, cutout, plan["shadow_dir"]))
        print(f"✅ Preview saved: {args.out}")


if __name__ == "__main__":
    main()
