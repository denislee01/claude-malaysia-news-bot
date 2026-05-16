"""Track posted stories in posted_urls.json to avoid duplicates."""
import json
import os
from pathlib import Path

_LOG_FILE = Path(__file__).parent / "posted_urls.json"


def get_posted_urls() -> set:
    """Return set of already-posted story URLs."""
    if not _LOG_FILE.exists():
        return set()
    try:
        data = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
        return set(data.get("urls", []))
    except Exception as e:
        print(f"[logger] Could not read {_LOG_FILE}: {e}")
        return set()


def log_posted(story: dict, ig_post_id: str, carousel: dict):
    """Append the posted story URL to the log file."""
    try:
        data = {"urls": []} if not _LOG_FILE.exists() else json.loads(_LOG_FILE.read_text(encoding="utf-8"))
        if story["url"] not in data["urls"]:
            data["urls"].append(story["url"])
        _LOG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[logger] Logged: {story['headline'][:60]}")
    except Exception as e:
        print(f"[logger] Failed to log story: {e}")


if __name__ == "__main__":
    urls = get_posted_urls()
    print(f"[logger] {len(urls)} stories already posted")
