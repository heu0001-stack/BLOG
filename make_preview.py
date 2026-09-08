"""
Builds a single-file HTML preview of every article in content/queue - title,
body, images, tags all together - so the queue can be reviewed at a glance
before manually pasting into the Naver Blog editor. Meant to be published as
a Claude Artifact after each run.

Usage: python make_preview.py [output_path.html]
Default output path is set for this session's scratchpad; pass a path to
write elsewhere.
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

from make_naver_export import html_to_text

ROOT = Path(__file__).parent
QUEUE_DIR = ROOT / "content" / "queue"
IMAGES_DIR = ROOT / "content" / "_images"

DEFAULT_OUT = Path(
    r"C:\Users\heu03\AppData\Local\Temp\claude\C--Users-heu03-blog-automation"
    r"\52aaaba1-8c3e-42ca-875a-0860935865c0\scratchpad\naver_review_desk.html"
)

PAGE_TEMPLATE = """<title>발행 검토대</title>
<style>
  :root {{
    --bg: #f0f1ec;
    --surface: #ffffff;
    --ink: #1e2321;
    --ink-soft: #565f5a;
    --accent: #3f6b52;
    --accent-soft: #dce7de;
    --line: #dad9ce;
    --meta: #8a6a2f;
    --shadow: 0 1px 2px rgba(30, 35, 33, 0.04), 0 8px 24px rgba(30, 35, 33, 0.05);
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #121712;
      --surface: #1b221c;
      --ink: #ecefe9;
      --ink-soft: #a3ada4;
      --accent: #86c6a1;
      --accent-soft: rgba(134, 198, 161, 0.14);
      --line: #2c342d;
      --meta: #d1ab6a;
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.35);
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #121712;
    --surface: #1b221c;
    --ink: #ecefe9;
    --ink-soft: #a3ada4;
    --accent: #86c6a1;
    --accent-soft: rgba(134, 198, 161, 0.14);
    --line: #2c342d;
    --meta: #d1ab6a;
    --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.35);
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
    -webkit-font-smoothing: antialiased;
  }}

  .wrap {{ max-width: 760px; margin: 0 auto; padding: 48px 20px 96px; }}

  .page-head {{ margin-bottom: 40px; }}
  .page-eyebrow {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--meta);
    margin: 0 0 10px;
  }}
  .page-head h1 {{
    font-family: "Gowun Batang", serif;
    font-size: clamp(28px, 4vw, 36px);
    margin: 0 0 8px;
    text-wrap: balance;
  }}
  .page-head p {{
    margin: 0;
    color: var(--ink-soft);
    font-size: 14.5px;
    line-height: 1.6;
    max-width: 56ch;
  }}

  .queue {{ display: flex; flex-direction: column; gap: 28px; }}

  .draft {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: var(--shadow);
    overflow: hidden;
  }}

  .draft-head {{ padding: 28px 32px 0; }}
  .draft-meta {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }}
  .draft-index {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    color: var(--ink-soft);
  }}
  .tag-row {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .tag {{
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent);
    font-weight: 600;
  }}
  .draft-title {{
    font-family: "Gowun Batang", serif;
    font-size: clamp(21px, 3vw, 26px);
    line-height: 1.4;
    margin: 0 0 22px;
    text-wrap: balance;
  }}

  .draft-body {{
    padding: 8px 32px 8px;
    font-size: 15.5px;
    line-height: 1.85;
    max-width: 62ch;
  }}
  .inline-figure {{ margin: 22px 0 24px; }}
  .inline-figure img {{
    display: block;
    width: 100%;
    max-height: 360px;
    object-fit: cover;
    border-radius: 10px;
  }}
  .inline-figure figcaption {{
    margin-top: 6px;
    font-size: 11.5px;
    color: var(--ink-soft);
    font-family: "JetBrains Mono", monospace;
  }}
  .draft-body h3 {{
    font-size: 16.5px;
    margin: 26px 0 8px;
    color: var(--accent);
  }}
  .draft-body p {{ margin: 0 0 14px; color: var(--ink); }}
  .draft-body strong {{ color: var(--ink); }}
  .draft-body em {{ color: var(--ink-soft); }}
  .draft-body a {{ color: var(--accent); text-decoration-color: var(--accent-soft); }}
  .draft-body table {{ border-collapse: collapse; width: 100%; margin: 4px 0 18px; font-size: 13.5px; }}
  .draft-body th, .draft-body td {{
    border: 1px solid var(--line);
    padding: 8px 10px;
    text-align: left;
  }}
  .draft-body th {{ background: var(--accent-soft); color: var(--accent); font-weight: 700; }}
  .table-scroll {{ overflow-x: auto; }}

  .draft-actions {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 32px 28px;
    border-top: 1px solid var(--line);
    margin-top: 20px;
  }}
  .copy-btn {{
    font-family: inherit;
    font-size: 13.5px;
    font-weight: 700;
    color: var(--surface);
    background: var(--accent);
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    cursor: pointer;
  }}
  .copy-btn:hover {{ filter: brightness(1.06); }}
  .copy-btn:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .copy-feedback {{
    font-size: 13px;
    color: var(--ink-soft);
    opacity: 0;
    transition: opacity 0.2s;
  }}
  .copy-feedback.show {{ opacity: 1; }}

  .empty {{
    background: var(--surface);
    border: 1px dashed var(--line);
    border-radius: 14px;
    padding: 48px 32px;
    text-align: center;
    color: var(--ink-soft);
  }}

  @media (prefers-reduced-motion: reduce) {{
    .copy-feedback {{ transition: none; }}
  }}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">

<div class="wrap">
  <div class="page-head">
    <p class="page-eyebrow">Naver Draft Queue</p>
    <h1>발행 검토대</h1>
    <p>게시 전 마지막 확인 자리입니다. 본문 복사 버튼으로 텍스트를 복사해 네이버 에디터에 붙여넣고, 이미지를 내려받아 함께 올린 뒤 게시하세요.</p>
  </div>
  <div class="queue">
{cards}
  </div>
</div>

<script>
  document.querySelectorAll(".copy-btn").forEach((btn) => {{
    btn.addEventListener("click", () => {{
      const ta = document.getElementById(btn.dataset.target);
      const feedback = btn.nextElementSibling;
      navigator.clipboard.writeText(ta.value).then(() => {{
        feedback.textContent = "복사됨";
        feedback.classList.add("show");
        setTimeout(() => feedback.classList.remove("show"), 1600);
      }}).catch(() => {{
        feedback.textContent = "복사 실패 - 직접 선택해 복사해주세요";
        feedback.classList.add("show");
      }});
    }});
  }});
</script>
"""

CARD_TEMPLATE = """    <article class="draft" id="draft-{slug}">
      <div class="draft-head">
        <div class="draft-meta">
          <span class="draft-index">Draft {n} of {total}</span>
          <div class="tag-row">{tags_html}</div>
        </div>
        <h1 class="draft-title">{title}</h1>
      </div>
      <div class="draft-body table-scroll">{content_html}</div>
      <div class="draft-actions">
        <button class="copy-btn" data-target="copy-{slug}">본문 복사</button>
        <span class="copy-feedback" aria-live="polite"></span>
      </div>
      <textarea id="copy-{slug}" hidden>{plain_text}</textarea>
    </article>"""


def load_credits(slug: str) -> dict:
    credit_path = IMAGES_DIR / f"{slug}_credits.txt"
    if not credit_path.exists():
        return {}
    out = {}
    for line in credit_path.read_text(encoding="utf-8").splitlines():
        if ": " in line:
            fname, rest = line.split(": ", 1)
            out[fname] = rest
    return out


def build_image_figure(img_path: Path, credits: dict) -> str:
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    credit = credits.get(img_path.name, "Pixabay")
    photographer = re.search(r"photo by (.+?) on Pixabay", credit)
    caption = f"사진: {photographer.group(1)}" if photographer else "Pixabay"
    return (
        f'<figure class="inline-figure"><img src="data:image/jpeg;base64,{b64}" alt="">'
        f"<figcaption>{html.escape(caption)}</figcaption></figure>"
    )


BLOCK_RE = re.compile(r"<(p|h3|table)\b.*?</\1>", re.S)


def build_content_with_images(content_html: str, slug: str) -> str:
    images = sorted(IMAGES_DIR.glob(f"{slug}_*.jpg"))
    blocks = [m.group(0) for m in BLOCK_RE.finditer(content_html)]
    if not images or not blocks:
        return content_html

    credits = load_credits(slug)
    figures = [build_image_figure(p, credits) for p in images]

    # first image right after the opening block; the rest spread out evenly
    # through the remaining body, each on its own, one per insertion point
    positions = {0: figures[0]}
    rest = figures[1:]
    used = {0}
    for i, fig in enumerate(rest):
        pos = round((i + 1) * len(blocks) / (len(rest) + 1))
        pos = max(1, min(pos, len(blocks) - 1))
        if blocks[pos].startswith("<h3"):
            pos = min(pos + 1, len(blocks) - 1)
        while pos in used and pos < len(blocks) - 1:
            pos += 1
        used.add(pos)
        positions[pos] = fig

    out = []
    for i, block in enumerate(blocks):
        out.append(block)
        if i in positions:
            out.append(positions[i])
    return "\n".join(out)


def build_card(article_path: Path, n: int, total: int) -> str:
    data = json.loads(article_path.read_text(encoding="utf-8"))
    slug = article_path.stem
    tags_html = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in data.get("labels", []))
    plain_text = data["title"] + "\n\n" + html_to_text(data["content"])
    return CARD_TEMPLATE.format(
        slug=slug,
        n=n,
        total=total,
        tags_html=tags_html,
        title=html.escape(data["title"]),
        content_html=build_content_with_images(data["content"], slug),
        plain_text=html.escape(plain_text),
    )


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    articles = sorted(QUEUE_DIR.glob("*.json"))

    if not articles:
        cards_html = '    <div class="empty">대기 중인 글이 없습니다.</div>'
    else:
        cards_html = "\n".join(
            build_card(a, i, len(articles)) for i, a in enumerate(articles, start=1)
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(PAGE_TEMPLATE.format(cards=cards_html), encoding="utf-8")
    print(f"DONE: {out_path} ({len(articles)} draft(s))")


if __name__ == "__main__":
    main()
