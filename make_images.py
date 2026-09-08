"""
Downloads free stock photos per queued article from Pixabay, based on the
article's labels/title, for manual upload into the Naver Blog editor.
Pixabay Content License: free for commercial use, no attribution required -
but the photographer/source URL is recorded in a sidecar *_credits.txt file
per article for reference anyway.

Usage:
  python make_images.py                      # process every article in content/queue
  python make_images.py content/queue/x.json  # process just this one
"""
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).parent
QUEUE_DIR = ROOT / "content" / "queue"
IMAGES_DIR = ROOT / "content" / "_images"
PIXABAY_URL = "https://pixabay.com/api/"
IMAGES_PER_ARTICLE = 3


def load_api_key() -> str:
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    key = config.get("pixabay_api_key", "")
    if not key or key == "PUT_YOUR_PIXABAY_API_KEY_HERE":
        print("ERROR: set pixabay_api_key in config.json first.")
        sys.exit(1)
    return key


GENERIC_LABELS = {"생활꿀팁", "생활정보", "정보", "꿀팁", "팁", "자취꿀팁", "가전추천", "가전"}


def search_query(data: dict) -> str:
    if data.get("image_query"):
        return data["image_query"]
    for label in data.get("labels", []):
        if label not in GENERIC_LABELS:
            return label
    return data["title"]


def fetch_images(api_key: str, query: str, count: int) -> list[dict]:
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "orientation": "horizontal",
        "per_page": max(count, 3),
        "lang": "ko",
    }
    r = requests.get(PIXABAY_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("hits", [])[:count]


def process(api_key: str, article_path: Path) -> None:
    data = json.loads(article_path.read_text(encoding="utf-8"))
    slug = article_path.stem
    if list(IMAGES_DIR.glob(f"{slug}_*.jpg")):
        print(f"SKIP {slug}: images already downloaded")
        return

    query = search_query(data)
    hits = fetch_images(api_key, query, IMAGES_PER_ARTICLE)
    if not hits:
        print(f"WARN {slug}: no Pixabay results for '{query}'")
        return

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credit_lines = []
    for i, hit in enumerate(hits):
        out_path = IMAGES_DIR / f"{slug}_{i}.jpg"
        out_path.write_bytes(requests.get(hit["largeImageURL"], timeout=30).content)
        credit_lines.append(
            f"{out_path.name}: photo by {hit['user']} on Pixabay - https://pixabay.com/photos/id-{hit['id']}/"
        )
        print(f"SAVED: {out_path}")

    (IMAGES_DIR / f"{slug}_credits.txt").write_text(
        "\n".join(credit_lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    api_key = load_api_key()
    targets = [Path(a) for a in sys.argv[1:]] or sorted(QUEUE_DIR.glob("*.json"))
    if not targets:
        print("No articles in content/queue.")
        return
    for article_path in targets:
        process(api_key, article_path)


if __name__ == "__main__":
    main()
