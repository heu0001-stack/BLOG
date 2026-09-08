"""
Converts every blog article (queued or already published to Blogger) into a
plain-text, paste-ready block for Naver Blog - which has no posting API, so
this stays a copy/paste step, but the writing/formatting work is automated.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
ARTICLE_DIRS = [ROOT / "content" / "queue", ROOT / "content" / "published"]
OUT_FILE = ROOT / "content" / "naver_export.txt"

DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."


def html_to_text(source: str) -> str:
    text = re.sub(r'<a href=\\?"([^"\\]+)\\?"[^>]*>(.*?)</a>', r"\2 (\1)", source)
    text = re.sub(r"</p>|<br>", "\n\n", text)
    text = re.sub(r"<h3>", "\n▶ ", text)
    text = re.sub(r"</h3>", "\n", text)
    text = re.sub(r"<tr>", "", text)
    text = re.sub(r"</tr>", "\n", text)
    text = re.sub(r"<t[hd]>", "", text)
    text = re.sub(r"</t[hd]>", " | ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"<em>|</em>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return html.unescape(text)


def main() -> None:
    seen = set()
    blocks = []
    for d in ARTICLE_DIRS:
        for f in sorted(d.glob("*.json")):
            if f.stem in seen:
                continue
            seen.add(f.stem)
            data = json.loads(f.read_text(encoding="utf-8"))
            body = html_to_text(data["content"])
            if "[COUPANG_LINK" in body:
                continue  # not ready - link not filled in yet
            has_affiliate_link = "coupang.com" in data["content"]
            block = (
                f"===== [{f.stem}] =====\n"
                f"제목: {data['title']}\n\n"
                f"{body}\n\n"
                + (f"{DISCLOSURE}\n" if has_affiliate_link else "")
                + f"태그: {' '.join(data.get('labels', []))}\n"
            )
            blocks.append(block)

    OUT_FILE.write_text("\n\n".join(blocks), encoding="utf-8")
    print(f"Wrote {OUT_FILE} ({len(blocks)} articles ready)")


if __name__ == "__main__":
    main()
