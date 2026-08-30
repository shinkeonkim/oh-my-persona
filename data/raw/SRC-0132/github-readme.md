# BOJ Problems Crawler

Crawls Baekjoon Online Judge problems into `problems/<id>/`.

## Output layout

- `problems/<id>/problem.md` — YAML frontmatter metadata:
  - `title`, `special_judge`, `time_limit`, `memory_limit`, `submissions`, `accepted`, `solved_users`, `acceptance_rate`, `collected_at`
- `problems/<id>/input-1.txt`, `output-1.txt`, `input-2.txt`, `output-2.txt`, …
- Downloaded images/attachments (e.g. `001_pic1.JPG`)
- Run log: `crawler.log`
- Error log: `logs.txt` — one line per entry: `<id>: <message>` (full crawl failures, per-asset failures, etc.)

### Assets (images / attachments)

- If the problem page loads successfully, `problem.md` and sample I/O files are always written.
- **`<a href="…">` plain links** (blog posts, other problems, random sites) are **not** downloaded; they stay as normal links in the markdown.
- Downloads are attempted for **media tags** (`img`, `embed`, `source`, `video`, `audio`, …) and for anchors only when the URL **looks like a file** (image/pdf/zip/etc.), matches BOJ upload/CDN paths, or the tag has a **`download`** attribute. **`iframe` / `object`** are fetched only when the URL looks like a direct file asset (not arbitrary HTML pages).
- For those URLs, the crawler tries several fetch strategies (Playwright request + stdlib `urllib`, multiple `Referer` / `Origin` / `User-Agent` combinations, longer timeouts).
- If every attempt fails, the markdown keeps the **original URL**; the failure is appended to `logs.txt`. Asset failures do **not** mark the whole problem as failed.
- Non-HTTP links (`tel:`, `data:`, …) are ignored for fetching (no download).

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager
- Playwright Chromium

## Setup

```bash
uv sync
uv run python -m playwright install chromium
```

## Usage

### Specific problems

Problem ids or short URLs (`http://boj.kr/<id>`):

```bash
uv run python main.py 1000 1010 http://boj.kr/1100
```

### All problems (problemset pagination)

Walks `https://www.acmicpc.net/problemset` and all `/problemset/<page>` pages.

```bash
uv run python main.py --all
```

### Concurrency

```bash
uv run python main.py --all --concurrency 5
```

- Problem page crawl concurrency: `--concurrency`
- Problem list (pagination) fetch concurrency: `2 × --concurrency`

## Skip already collected

- By default, skips when `problems/<id>/problem.md` exists and is non-empty.
- Force re-fetch: `--force`

```bash
uv run python main.py --all --force
```

## Logs

- `crawler.log`: structured run progress (start, discovery, skip counts, per-problem crawl, summary).
- `logs.txt`: cleared at the start of each run; append-only during the run. Empty if nothing failed.
