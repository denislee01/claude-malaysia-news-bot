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

import scraper
import selector
import image_gen
import builder
import poster
import logger


def run(dry_run: bool = False):
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")

    # 1. Scrape
    print("\n── STEP 1: SCRAPE ──")
    stories = scraper.run()
    if not stories:
        print("[pipeline] No stories scraped — exiting.")
        sys.exit(0)

    # 2. Get posted URLs for dedup
    print("\n── STEP 2: DEDUP CHECK ──")
    posted_urls = logger.get_posted_urls()
    print(f"[pipeline] {len(posted_urls)} already-posted URLs loaded")

    # 3. Select + write
    print("\n── STEP 3: SELECT + WRITE ──")
    pairs = selector.run(stories, posted_urls)
    if not pairs:
        print("[pipeline] No fresh stories to post — exiting.")
        sys.exit(0)

    # Post only the first pair this run (second pair = next scheduled run)
    story, carousel = pairs[0]
    print(f"\n[pipeline] Selected: {story['headline'][:70]}")

    # Cover slide always uses Pexels with Claude's cinematic cover_image_prompt.
    # Article og:images (logos, brand graphics, flat screenshots) are not bold
    # enough for Instagram — Pexels gives us dramatic, unique photos every run.

    # 4. Generate images
    print("\n── STEP 4: IMAGE GENERATION ──")
    img_dir = f"/tmp/cm_imgs_{run_ts}"
    image_paths = image_gen.generate_slide_images(carousel, img_dir)

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
    logger.log_posted(story, submission_id, carousel)

    print(f"\n✓ DONE — Posted: {story['headline'][:60]}")
    print(f"  Submission ID: {submission_id}")
    print(f"  Slides at: ~/Downloads/carousels/cm-{run_id}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Build but don't post")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
