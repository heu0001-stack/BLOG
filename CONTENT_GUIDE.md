# Naver Blog Content Guide

This repo prepares (but does not publish) posts for a Naver Blog. Naver has no
posting API, so a human copies the finished text from the published "발행
검토대" Artifact into Naver's editor and posts it manually. Your job as the
scheduled agent is to add ONE new ready-to-review article per run, plus its
images, then update that Artifact.

## Target audience

50대 여성 (Korean women in their 50s) who read Naver Blog often. Write in warm
해요체, not curt 합니다체. Practical and specific over abstract. Avoid content
that reads like generic filler - see "Content quality bar" below.

## Topic priority (check in this order)

1. **Government subsidies/benefits/policy support** (지원금, 혜택, 대책) that
   are currently timely - e.g. a seasonal 민생안정대책, a new subsidy program,
   a deadline-bound benefit. Search for this first, every run. If you find a
   genuinely current, verifiable one not already covered by an existing file
   in `content/queue/` or `content/posted/`, use it.
2. If no good government-benefit topic exists right now, fall back to this
   rotation based on the slot you were told you're filling:
   - Weekday slot 1: 생활꿀팁 (practical household/life tips, can be seasonal)
   - Weekday slot 2: 반려동물팁 (pet care tips)
   - Weekend slot: 재미글 (a warm, relatable read - not youth meme humor;
     think 공감형 에세이 or a "좋은글" style piece this audience shares)

Before writing, list the existing slugs in `content/queue/` and
`content/posted/` and pick a topic that isn't a near-duplicate of one already
there.

## Content quality bar

- No fabricated first-person experience ("제가 3개월 써보니...", "우리 강아지가...").
  Write as information delivery, not a fake personal review.
- Don't just restate common-knowledge advice. Include something specific:
  exact numbers, dates, legal thresholds, or a genuinely current fact - not
  vague "많이", "보통" filler. If you can't find a specific angle, keep
  researching before writing.
- Any government subsidy/benefit article MUST include a "참고 자료" section
  at the end of the `content` HTML with real links: the relevant ministry's
  official site (e.g. mofe.go.kr, mafra.go.kr) plus 1-2 dated mainstream news
  articles. Verify each source's actual publish date by fetching it - search
  snippets can misrepresent the year (a "2026" titled page has turned out to
  be a republished 2025 article before). Do not cite obvious content-farm/SEO
  spam sites even if they rank highly.

## File format

Add one file to `content/queue/`, named `NNN_slug.json` where NNN is the next
unused 3-digit number across both `content/queue/` and `content/posted/`:

```json
{
  "title": "...",
  "labels": ["생활꿀팁", "구체적주제", "..."],
  "image_query": "english search term for Pixabay (optional)",
  "content": "<p>...</p><h3>...</h3>...<h3>참고 자료</h3><p>...</p>"
}
```

`content` is raw HTML using only `<p>`, `<h3>`, `<table><tr><th>/<td></table>`,
`<strong>`, `<em>`, `<a href="...">`. `labels` should include one broad
category tag (생활꿀팁/반려동물팁/재미글) plus specific topic tags.
`image_query` overrides the auto image search term when the labels/title
aren't good visual search terms (e.g. Korean cultural terms often return
irrelevant Pixabay results - use a descriptive English term instead).

## Steps for each run

1. `git pull` first in case anything changed.
2. Decide the topic per the priority rules above (research with web search as
   needed - verify facts, verify source dates).
3. Write the new `content/queue/NNN_slug.json`.
4. Run `python make_images.py` (needs `pixabay_api_key` - see note below) to
   fetch 3 images for the new article only.
5. Run `python make_naver_export.py` and `python make_preview.py`.
6. Publish the review desk: call the Artifact tool with `action: "read"` on
   `https://claude.ai/code/artifact/392c93a1-d5e9-408f-9fc4-638c5854f9c7`
   first (required before updating an artifact this session hasn't published
   before), then `action: "publish"` with that same `url` and
   `file_path` pointing at the `make_preview.py` output, with a short `note`
   describing what was added.
7. `git add`, commit (message: what article was added), and `git push`.

## Pixabay API key

`config.json` is gitignored (it holds a real API key) so it won't be in this
repo. The key will be given to you directly in the run prompt when the
routine fires - write it into `config.json` (see `config.example.json` for
the shape) at the start of the run if that file doesn't already exist.
