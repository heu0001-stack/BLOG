# 네이버 블로그 콘텐츠 준비 파이프라인

50대 여성을 타겟으로 하는 네이버 블로그의 글감을 준비하는 자동화입니다.
네이버는 포스팅 API가 없어서 **발행은 사람이 직접** 합니다 — 이 파이프라인은
주제 리서치·작성·이미지 준비·검토까지만 자동화합니다.

콘텐츠 원칙과 자동화 실행 절차는 [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md)를 보세요.

## 로컬에서 수동으로 돌리는 법

```powershell
.\.venv\Scripts\python.exe make_images.py       # content/queue의 새 글에 Pixabay 이미지 3장 다운로드
.\.venv\Scripts\python.exe make_naver_export.py # 네이버 붙여넣기용 텍스트 생성 (content/naver_export.txt)
.\.venv\Scripts\python.exe make_preview.py      # 검토용 미리보기 HTML 생성 → Artifact로 게시
```

`config.json`이 필요합니다 (`config.example.json` 참고, `pixabay_api_key` 채워서
같은 폴더에 `config.json`으로 저장 — 이 파일은 git에 커밋되지 않습니다).

## 폴더 구조

- `content/queue/*.json` — 아직 게시 안 한 글 (title/labels/content/image_query)
- `content/posted/` — 실제로 네이버에 올린 글은 여기로 옮겨서 큐에서 제외
- `content/_images/` — 글마다 3장씩 받은 Pixabay 이미지 + 출처 기록
- `_archive_blogger/` — 이전 Blogger + 가전 리뷰 방향의 유산 (git 대상 아님, 로컬 보관용)

## 발행 검토대

준비된 글은 매번 같은 Artifact 링크에서 확인합니다:
https://claude.ai/code/artifact/392c93a1-d5e9-408f-9fc4-638c5854f9c7

여기서 본문을 복사해 네이버 에디터에 붙여넣고, 이미지를 올린 뒤 직접 게시하면
됩니다. 게시를 마친 글은 `content/queue`에서 `content/posted`로 옮겨주세요.
