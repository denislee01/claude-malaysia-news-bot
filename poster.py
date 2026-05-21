"""Upload slides to ImgBB and post carousel to Instagram via Graph API."""
import os
import time
import requests

IMGBB_API_KEY = os.environ["IMGBB_API_KEY"]
IG_USER_ID = os.environ["IG_USER_ID"]
IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
GRAPH_BASE = "https://graph.instagram.com/v19.0"


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


def create_image_container(image_url: str, is_carousel_item: bool = True) -> str:
    """Create an IG media container for one image. Returns container ID."""
    params = {
        "image_url": image_url,
        "access_token": IG_ACCESS_TOKEN,
    }
    if is_carousel_item:
        params["is_carousel_item"] = "true"

    resp = requests.post(
        f"{GRAPH_BASE}/{IG_USER_ID}/media",
        params=params,
        timeout=30,
    )
    if not resp.ok:
        print(f"[poster] IG API error {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    container_id = resp.json()["id"]
    print(f"[poster] IG container created: {container_id}")
    return container_id


def create_carousel_container(children_ids: list[str], caption: str) -> str:
    """Create an IG carousel container referencing all image containers."""
    resp = requests.post(
        f"{GRAPH_BASE}/{IG_USER_ID}/media",
        params={
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=30,
    )
    resp.raise_for_status()
    carousel_id = resp.json()["id"]
    print(f"[poster] Carousel container: {carousel_id}")
    return carousel_id


def publish_container(container_id: str) -> str:
    """Publish a media container. Returns the published post ID."""
    resp = requests.post(
        f"{GRAPH_BASE}/{IG_USER_ID}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=30,
    )
    resp.raise_for_status()
    post_id = resp.json()["id"]
    print(f"[poster] Published! post_id={post_id}")
    return post_id


def run(image_paths: list[str], caption: str, account_id: str = None) -> str:
    """Full post flow: upload → create containers → carousel → publish."""
    print(f"[poster] Uploading {len(image_paths)} slides to ImgBB...")
    public_urls = []
    for path in image_paths:
        url = upload_image_to_imgbb(path)
        public_urls.append(url)
        time.sleep(0.5)

    print(f"[poster] Creating IG media containers...")
    children_ids = []
    for url in public_urls:
        cid = create_image_container(url, is_carousel_item=True)
        children_ids.append(cid)
        time.sleep(1)

    print(f"[poster] Creating carousel container...")
    carousel_id = create_carousel_container(children_ids, caption)
    time.sleep(2)

    print(f"[poster] Publishing carousel...")
    post_id = publish_container(carousel_id)
    return post_id


if __name__ == "__main__":
    print("[poster] Module loaded — run via pipeline.py")
