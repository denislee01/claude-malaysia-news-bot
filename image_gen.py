"""Fetch carousel slide background images from Pexels API — free, real photos."""
import os
import io
import random
import requests
from pathlib import Path
from PIL import Image, ImageDraw


def _fetch_url_image(url: str) -> bytes | None:
    """Download an image directly from a URL (e.g. article og:image)."""
    try:
        resp = requests.get(
            url, timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" in content_type:
            return resp.content
        print(f"[image_gen] og:image URL not an image (content-type: {content_type})")
        return None
    except Exception as e:
        print(f"[image_gen] og:image download failed: {e}")
        return None

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

# 1080x1350 px Instagram portrait (4:5)
WIDTH, HEIGHT = 1080, 1350

# Default search queries per slide position (used as fallback if no image_prompt)
# Slides 1 and 10 try Malaysia first, then fall back to neutral
# All other slides use neutral queries that won't accidentally show wrong-country imagery
# Queries chosen for cinematic drama — bold, moody, visually striking on Instagram
_DEFAULT_QUERIES = [
    "Kuala Lumpur KLCC night aerial",           # slide 1  cover  (MY-specific)
    "server room blue glow technology dark",    # slide 2  WHAT HAPPENED
    "Kuala Lumpur skyline golden sunset",       # slide 3  MY angle (MY-specific)
    "rain window city lights bokeh night",      # slide 4  THE NUMBER
    "silhouette dramatic spotlight empty stage",# slide 5  MOST PEOPLE DON'T KNOW
    "speaker stage spotlight crowd dark",       # slide 6  EXPERT TAKE
    "light trail highway night long exposure",  # slide 7  HOW WE GOT HERE
    "person laptop night window city view",     # slide 8  WHAT TO DO NOW
    "storm clouds lightning dramatic dark sky", # slide 9  WATCH OUT FOR
    "Kuala Lumpur skyline night city lights",   # slide 10 CTA (MY-specific)
]

# Neutral fallback queries used when SG-specific search returns no results
_NEUTRAL_FALLBACK_QUERIES = [
    "city aerial night lights dramatic",        # slide 1  fallback
    "server room blue glow technology dark",    # slide 2
    "modern city skyline golden sunset",        # slide 3  fallback
    "rain window city lights bokeh night",      # slide 4
    "silhouette dramatic spotlight empty stage",# slide 5
    "speaker stage spotlight crowd dark",       # slide 6
    "light trail highway night long exposure",  # slide 7
    "person laptop night window city view",     # slide 8
    "storm clouds lightning dramatic dark sky", # slide 9
    "city skyline night dramatic lights",       # slide 10 fallback
]

# Slides that are Malaysia-specific and should try a neutral fallback if no MY results
_SG_SPECIFIC_SLIDE_INDICES = {0, 2, 9}


def _prompt_to_query(prompt: str, allow_singapore: bool = False) -> str:
    """Trim an image_prompt into a short Pexels-friendly search query.

    By default strips country/location words to avoid wrong-country photo results.
    Set allow_singapore=True for cover and SG-angle slides.
    """
    stop = {
        "dark", "dramatic", "no", "text", "portrait", "orientation",
        "cinematic", "moody", "amber", "glow", "glowing", "wide", "angle",
        "close", "up", "bleed", "shot", "background", "lighting", "light",
        "with", "and", "the", "for", "a", "an", "in", "of", "at", "on",
        "9:16", "3:4", "full", "side", "view",
    }
    # Strip country/place names unless this is a Malaysia-specific slide
    location_words = {
        "singapore", "malaysia", "america", "american", "usa", "us",
        "china", "chinese", "india", "indian", "australia", "australian",
        "uk", "british", "european", "europe",
    }
    if not allow_singapore:
        stop |= location_words

    words = [w.strip(",.;:()") for w in prompt.lower().split()]
    filtered = [w for w in words if w and w not in stop and len(w) > 2]
    return " ".join(filtered[:5])


def _fetch_pexels(query: str, slide_index: int, fallback_query: str | None = None) -> bytes | None:
    """Call Pexels search API and return raw image bytes, or None on failure.

    If fallback_query is provided and the primary query returns no results,
    automatically retries with the fallback query.
    """
    if not PEXELS_API_KEY:
        return None

    def _search(q: str) -> bytes | None:
        try:
            # Random page (1-5) so each run gets a different set of photos — 75 photo pool
            page = random.randint(1, 5)
            resp = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": q,
                    "per_page": 15,
                    "page": page,
                    "orientation": "portrait",
                    "size": "large",
                },
                timeout=15,
            )
            resp.raise_for_status()
            photos = resp.json().get("photos", [])
            if not photos:
                # Try page 1 as fallback if random page had no results
                if page > 1:
                    resp = requests.get(
                        "https://api.pexels.com/v1/search",
                        headers={"Authorization": PEXELS_API_KEY},
                        params={
                            "query": q,
                            "per_page": 15,
                            "page": 1,
                            "orientation": "portrait",
                            "size": "large",
                        },
                        timeout=15,
                    )
                    resp.raise_for_status()
                    photos = resp.json().get("photos", [])
                if not photos:
                    print(f"[image_gen] Pexels: no results for '{q}'")
                    return None
            # Pick a random photo from the pool so slides vary between runs
            photo = random.choice(photos)
            img_url = photo["src"]["large2x"]
            img_resp = requests.get(img_url, timeout=30)
            img_resp.raise_for_status()
            print(f"[image_gen] Pexels: '{q}' (page {page}) → {img_url[:60]}...")
            return img_resp.content
        except Exception as e:
            print(f"[image_gen] Pexels error for '{q}': {e}")
            return None

    result = _search(query)
    if result is None and fallback_query and fallback_query != query:
        print(f"[image_gen] Retrying with neutral fallback: '{fallback_query}'")
        result = _search(fallback_query)
    return result


def _crop_and_resize(img_bytes: bytes, path: str):
    """Crop image to 4:5 ratio and resize to 1080x1350, save as JPEG."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    target_ratio = WIDTH / HEIGHT  # 0.8

    if w / h > target_ratio:
        # Too wide — crop sides
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        # Too tall — crop top/bottom
        new_h = int(w / target_ratio)
        top = (h - new_h) // 3  # bias toward top of image
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    img.save(path, "JPEG", quality=92)


def _gradient_fallback(path: str, slide_index: int):
    """Dark gradient fallback if Pexels unavailable."""
    palettes = [
        ((10, 10, 30), (25, 20, 60)),
        ((5, 20, 25), (10, 45, 55)),
        ((20, 10, 10), (50, 20, 15)),
        ((10, 15, 10), (20, 40, 20)),
        ((20, 10, 25), (45, 15, 55)),
        ((15, 10, 5), (45, 30, 10)),
        ((5, 5, 20), (15, 15, 50)),
        ((20, 5, 15), (55, 10, 35)),
        ((5, 20, 20), (10, 50, 50)),
        ((10, 10, 10), (30, 25, 5)),
    ]
    top, bottom = palettes[slide_index % len(palettes)]
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    img.save(path, "JPEG", quality=92)


def generate_slide_images(carousel: dict, output_dir: str) -> list[str]:
    """Fetch 10 Pexels photos (or gradient fallback) for the carousel slides."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    paths = []

    # Build query list from carousel prompts
    queries = []

    # Slide 1 — cover (index 0, MY-specific → allow Malaysia in query)
    cover_prompt = carousel.get("cover_image_prompt", "")
    queries.append(_prompt_to_query(cover_prompt, allow_singapore=True) if cover_prompt else _DEFAULT_QUERIES[0])

    # Slides 2–9 — inner
    # Slide 3 is "THE MALAYSIA ANGLE" → index 2 in queries, allow Malaysia
    for i, slide in enumerate(carousel.get("slides", [])):
        prompt = slide.get("image_prompt", "")
        query_idx = i + 1  # query index (0=cover, 1=slide2, 2=slide3, ...)
        is_sg_slide = query_idx in _SG_SPECIFIC_SLIDE_INDICES
        queries.append(
            _prompt_to_query(prompt, allow_singapore=is_sg_slide) if prompt
            else _DEFAULT_QUERIES[min(i + 1, 8)]
        )

    # Slide 10 — CTA (index 9, MY-specific)
    queries.append(_DEFAULT_QUERIES[9])

    # Pad / trim to exactly 10
    while len(queries) < 10:
        queries.append(_DEFAULT_QUERIES[len(queries) % len(_DEFAULT_QUERIES)])
    queries = queries[:10]

    for i, query in enumerate(queries):
        path = os.path.join(output_dir, f"slide_{i+1:02d}.jpg")

        # All slides — Pexels only. Article og:images (logos, brand graphics,
        # flat screenshots) are not bold or cinematic enough for Instagram covers.
        # Claude's cover_image_prompt already generates dramatic scene descriptions.
        neutral_fallback = _NEUTRAL_FALLBACK_QUERIES[i] if i in _SG_SPECIFIC_SLIDE_INDICES else None
        img_bytes = _fetch_pexels(query, slide_index=i, fallback_query=neutral_fallback)
        if img_bytes:
            _crop_and_resize(img_bytes, path)
        else:
            print(f"[image_gen] Using gradient fallback for slide {i+1}")
            _gradient_fallback(path, i)
        paths.append(path)

    print(f"[image_gen] Generated {len(paths)} slide images in {output_dir}")
    return paths


if __name__ == "__main__":
    paths = generate_slide_images({}, "/tmp/cs_test_run")
    print(paths)
