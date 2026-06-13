#!/usr/bin/env python3
"""Daily IELTS Essential Word — english.v4vendetta.sbs"""

import html
import json
import os
import threading
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fetcher import fetch_word
from update_daily import cache_path, update_day, word_index_for

PORT = int(os.environ.get("PORT", "8092"))
BASE = Path(__file__).parent
WORDS = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
START = date(2026, 1, 1)
_fetch_lock = threading.Lock()


def load_cached(d: date) -> dict | None:
    path = cache_path(d)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_word_data(d: date) -> dict:
    cached = load_cached(d)
    if cached:
        return cached

    idx = word_index_for(d)
    local = WORDS[idx]
    with _fetch_lock:
        cached = load_cached(d)
        if cached:
            return cached
        try:
            update_day(d, force=False)
            cached = load_cached(d)
            if cached:
                return cached
        except Exception as exc:
            print(f"[app] fetch failed for {d}: {exc}")

    enriched = fetch_word(local["word"], local)
    return {
        "date": d.isoformat(),
        "num": idx + 1,
        "total": len(WORDS),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        **enriched,
    }


def render_page(data: dict, day: date, offset: int = 0) -> str:
    word = html.escape(data["word"])
    pos = html.escape(data.get("pos", ""))
    definition = html.escape(data.get("definition", ""))
    fa = data.get("fa", "")
    fa_block = f'<p class="fa">{html.escape(fa)}</p>' if fa else ""
    phonetic = data.get("phonetic", "")
    phon_block = f'<p class="phonetic">{html.escape(phonetic)}</p>' if phonetic else ""

    examples = data.get("examples", [])
    if examples and isinstance(examples[0], str):
        examples = [{"text": ex, "source": "IELTS Essential Words"} for ex in examples]

    ex_html = ""
    for ex in examples:
        text = html.escape(ex.get("text", ""))
        src = html.escape(ex.get("source", ""))
        ex_html += f'<li><span class="ex-text">"{text}"</span><span class="ex-src">— {src}</span></li>'

    sources = data.get("sources", [])
    src_html = ""
    for src in sources:
        name = html.escape(src.get("name", ""))
        url = html.escape(src.get("url", ""))
        src_html += f'<a href="{url}" target="_blank" rel="noopener" class="source-tag">{name}</a>'

    fetched = data.get("fetched_at", "")
    if fetched:
        try:
            ts = datetime.fromisoformat(fetched.replace("Z", "+00:00"))
            fetched_label = ts.strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            fetched_label = fetched[:16]
    else:
        fetched_label = "—"

    online_badge = "Live from web" if data.get("online") else "Local fallback"
    num = data.get("num", 0)
    total = data.get("total", len(WORDS))

    prev_off = offset - 1
    next_off = offset + 1
    prev_link = f'<a href="/?offset={prev_off}" class="nav-btn">← دیروز</a>' if offset > 0 else ""
    next_link = f'<a href="/?offset={next_off}" class="nav-btn">فردا →</a>'

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{word} — IELTS Word of the Day</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0f1419;
  --card: #1a2332;
  --accent: #3b82f6;
  --accent2: #60a5fa;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --border: #2d3a4f;
  --green: #34d399;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background-image: radial-gradient(ellipse at 20% 0%, rgba(59,130,246,.12) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 100%, rgba(96,165,250,.08) 0%, transparent 50%);
}}
.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 25px 50px rgba(0,0,0,.4);
}}
.badge-row {{ display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
.badge {{
  display: inline-block;
  background: rgba(59,130,246,.15);
  color: var(--accent2);
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
  padding: .35rem .75rem;
  border-radius: 999px;
}}
.badge.live {{ background: rgba(52,211,153,.15); color: var(--green); }}
.word {{
  font-family: 'DM Serif Display', serif;
  font-size: 3rem;
  color: #fff;
  line-height: 1.1;
  margin-bottom: .25rem;
}}
.phonetic {{ color: var(--muted); font-size: .95rem; margin-bottom: .25rem; }}
.pos {{ color: var(--muted); font-style: italic; font-size: .95rem; margin-bottom: 1.5rem; }}
.definition {{ font-size: 1.1rem; line-height: 1.65; margin-bottom: 1rem; }}
.fa {{
  font-size: 1rem; color: var(--accent2); direction: rtl; text-align: right;
  margin-bottom: 1.5rem; padding: .75rem 1rem;
  background: rgba(59,130,246,.08); border-radius: 10px; border-right: 3px solid var(--accent);
}}
.examples-title {{
  font-size: .8rem; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); margin-bottom: .75rem;
}}
.examples {{ list-style: none; }}
.examples li {{
  padding: .75rem 0; border-bottom: 1px solid var(--border);
  font-size: .93rem; line-height: 1.55;
}}
.examples li:last-child {{ border-bottom: none; }}
.ex-text {{ color: #cbd5e1; display: block; margin-bottom: .25rem; }}
.ex-src {{ color: var(--muted); font-size: .78rem; }}
.sources {{
  margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border);
}}
.sources-title {{
  font-size: .75rem; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); margin-bottom: .6rem;
}}
.source-tags {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .5rem; }}
.source-tag {{
  font-size: .75rem; color: var(--accent2); text-decoration: none;
  padding: .3rem .65rem; border: 1px solid var(--border); border-radius: 999px;
  transition: background .2s;
}}
.source-tag:hover {{ background: rgba(59,130,246,.12); }}
.updated {{ font-size: .72rem; color: var(--muted); }}
.meta {{
  margin-top: 1.25rem; padding-top: 1.25rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: .75rem; font-size: .82rem; color: var(--muted);
}}
.nav {{ display: flex; gap: .5rem; }}
.nav-btn {{
  color: var(--accent2); text-decoration: none; padding: .4rem .75rem;
  border: 1px solid var(--border); border-radius: 8px; font-size: .82rem;
  transition: background .2s;
}}
.nav-btn:hover {{ background: rgba(59,130,246,.1); }}
footer {{ text-align: center; margin-top: 1.5rem; font-size: .75rem; color: var(--muted); }}
</style>
</head>
<body>
<div>
  <div class="card">
    <div class="badge-row">
      <span class="badge">IELTS Essential Words · {day.strftime("%B %d, %Y")}</span>
      <span class="badge live">{online_badge}</span>
    </div>
    <h1 class="word">{word}</h1>
    {phon_block}
    <p class="pos">{pos}</p>
    <p class="definition">{definition}</p>
    {fa_block}
    <p class="examples-title">Examples</p>
    <ul class="examples">{ex_html}</ul>
    <div class="sources">
      <p class="sources-title">Sources</p>
      <div class="source-tags">{src_html}</div>
      <p class="updated">Updated: {html.escape(fetched_label)}</p>
    </div>
    <div class="meta">
      <span>Word {num} of {total}</span>
      <div class="nav">{prev_link}{next_link}</div>
    </div>
  </div>
  <footer>english.v4vendetta.sbs — یک کلمه در روز</footer>
</div>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _build_response(self):
        parsed = urlparse(self.path)
        if parsed.path not in ("/", "/index.html"):
            return None

        qs = parse_qs(parsed.query)
        offset = int(qs.get("offset", ["0"])[0])
        day = date.fromordinal(
            START.toordinal() + (date.today().toordinal() - START.toordinal()) + offset
        )
        data = get_word_data(day)
        return render_page(data, day, offset).encode("utf-8")

    def do_GET(self):
        body = self._build_response()
        if body is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        body = self._build_response()
        if body is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {args[0]}")


def main():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"IELTS Daily Word running on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
