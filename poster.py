"""Upload slides to ImgBB then post carousel to Instagram via Blotato API."""
import os
import time
import requests

IMGBB_API_KEY    = os.environ["IMGBB_API_KEY"]
BLOTATO_API_KEY  = os.environ["BLOTATO_API_KEY"]
BLOTATO_ACCOUNT_ID = os.environ["BLOTATO_ACCOUNT_ID"]
BLOTATO_BASE     = "https://backend.blotato.com/v2"


def upload_image_to_imgbb(image_path: str) -> str:
    """Upload one image to ImgBB and return its public URL."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": f},
            timeout=30,
        )
    resp.raise_for_status()
    url = resp.json()["data"]["url"]
    print(f"[poster] ImgBB upload: {os.path.basename(image_path)} → {url[:60]}...")
    return url


def post_carousel(image_urls: list[str], caption: str) -> str:
    """Post a carousel to Instagram via Blotato. Returns post ID."""
    resp = requests.post(
        f"{BLOTATO_BASE}/posts",
        headers={
            "Content-Type": "application/json",
            "blotato-api-key": BLOTATO_API_KEY,
        },
        json={
            "post": {
                "accountId": BLOTATO_ACCOUNT_ID,
                "content": {
                    "text": caption,
                    "mediaUrls": image_urls,
                    "platform": "instagram",
                },
                "target": {"targetType": "instagram"},
            }
        },
        timeout=60,
    )
    if not resp.ok:
        print(f"[poster] Blotato error {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    post_id = resp.json().get("id", "unknown")
    print(f"[poster] Published! post_id={post_id}")
    return post_id


def run(image_paths: list[str], caption: str, account_id: str = None) -> str:
    """Full post flow: upload to ImgBB → post via Blotato."""
    print(f"[poster] Uploading {len(image_paths)} slides to ImgBB...")
    public_urls = []
    for path in image_paths:
        url = upload_image_to_imgbb(path)
        public_urls.append(url)
        time.sleep(0.5)

    print(f"[poster] Posting carousel via Blotato...")
    post_id = post_carousel(public_urls, caption)
    return post_id


if __name__ == "__main__":
    print("[poster] Module loaded — run via pipeline.py")
