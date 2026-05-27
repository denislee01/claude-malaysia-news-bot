"""
Main pipeline orchestrator — runs the full flow:
  scraper → selector → image_gen → builder → poster → logger

Run manually: python pipeline.py
GitHub Actions runs this 2x/day automatically.
"""
import os
import sys
import argparse
from datetime import datetime, timezone

import requests
import scraper
import selector
import image_gen
import builder
import poster
import logger


def _hours_since_last_ig_post() -> float:
    """Query Instagram directly for the actual last post time — never lies even if git commit failed."""
    ig_user_id = os.environ.get("IG_USER_ID", "")
    ig_token = os.environ.get("IG_ACCESS_TOKEN", "")
    if not ig_user_id or not ig_token:
        return 999.0
    try:
        resp = requests.get(
            f"https://graph.instagram.com/v19.0/{ig_user_id}/media",
            params={"fields": "timestamp", "limit": 1, "access_token": ig_token},
            timeout=10,
        )
        data = resp.json()
        posts = data.get("data", [])
        if not posts:
            return 999.0
        last_ts = datetime.fromisoformat(posts[0]["timestamp"].replace("Z", "+00:00"))
        hours = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
        print(f"[pipeline] IG API: last post was {hours:.1f}h ago")
        return hours
    except Exception as e:
        print(f"[pipeline] IG API check failed: {e} — falling back to local log")
        return 999.0


def run(dry_run: bool = False):
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")

    # 1. Scrape
    print("\n── STEP 1: SCRAPE ──")
    stories = scraper.run()
    if not stories:
        print("[pipeline] No stories scraped — exiting.")
        sys.exit(0)

    # 2. Get posted URLs for dedup + skip if already posted this window
    print("\n── STEP 2: DEDUP CHECK ──")
    posted_urls = logger.get_posted_urls()
    print(f"[pipeline] {len(posted_urls)} already-posted URLs loaded")

    # Check IG API first (authoritative — works even when git commit failed last run)
    hours_ago = _hours_since_last_ig_post()
    # Fall back to local log if IG API unavailable
    if hours_ago == 999.0:
        hours_ago = logger.hours_since_last_post()
        print(f"[pipeline] Local log: last post was {hours_ago:.1f}h ago")

    if not dry_run and hours_ago < 7:
        print(f"[pipeline] Already posted {hours_ago:.1f}h ago — skipping to avoid double-post.")
        sys.exit(0)

    # 3. Select + write
    print("\n── STEP 3: SELECT + WRITE ──")
    pairs = selector.run(stories, posted_urls)
    if not pairs:
        print("[pipeline] No fresh stories to post — exiting.")
        sys.exit(0)

    # Post only the first pair this run (second pair = next scheduled run)
    story, carousel = pairs[0]
    print(f"\n[pipeline] Selected: {story['headline'][:70]}")

    # 4. Generate images — use article og:image for cover if available (real person/CEO photos)
    print("\n── STEP 4: IMAGE GENERATION ──")
    img_dir = f"/tmp/cm_imgs_{run_ts}"
    og_url  = story.get("og_image_url", "")
    used_img_urls = logger.get_used_img_urls()
    image_paths, new_img_urls = image_gen.generate_slide_images(
        carousel, img_dir, og_image_url=og_url, used_img_urls=used_img_urls
    )

    # Pad to 10 images if fewer generated
    while len(image_paths) < 10:
        image_paths.append(image_paths[-1])
    image_paths = image_paths[:10]

    # 5. Build HTML → export PNGs
    print("\n── STEP 5: BUILD CAROUSEL ──")
    run_id = f"{run_ts}_{story.get('category','ai')}"
    png_paths = builder.run(carousel, image_paths, run_id)

    if dry_run:
        print(f"\n[pipeline] DRY RUN — skipping post. PNGs at: ~/Downloads/carousels/cm-{run_id}/")
        return

    # 6. Post
    print("\n── STEP 6: POST ──")
    caption = carousel.get("caption", "")
    submission_id = poster.run(png_paths, caption)

    # 7. Log
    print("\n── STEP 7: LOG ──")
    logger.log_posted(story, submission_id, carousel, new_img_urls=new_img_urls)

    print(f"\n✓ DONE — Posted: {story['headline'][:60]}")
    print(f"  Submission ID: {submission_id}")
    print(f"  Slides at: ~/Downloads/carousels/cm-{run_id}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Build but don't post")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
