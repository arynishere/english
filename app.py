#!/usr/bin/env python3
"""Daily IELTS Essential Word — english.v4vendetta.sbs"""

import json
import os
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "8092"))
BASE = Path(__file__).parent
WORDS = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
START = date(2026, 1, 1)


def word_for_day(d: date | None = None) -> tuple[dict, int, int]:
    d = d or date.today()
    idx = (d.toordinal() - START.toordinal()) % len(WORDS)
    return WORDS[idx], idx + 1, len(WORDS)


def word_for_offset(offset: int) -> tuple[dict, int, int]:
    d = date.fromordinal(START.toordinal() + offset)
    return word_for_day(d)


def render_page(word: dict, num: int, total: int, day: date, offset: int = 0) -> str:
    pos = word.get("pos", "")
    examples = word.get("examples", [])
    ex_html = "".join(f'<li>"{e}"</li>' for e in examples)
    fa = word.get("fa", "")
    fa_block = f'<p class="fa">{fa}</p>' if fa else ""

    prev_off = offset - 1
    next_off = offset + 1
    prev_link = f'<a href="/?offset={prev_off}" class="nav-btn">← دیروز</a>' if offset > 0 else ""
    next_link = f'<a href="/?offset={next_off}" class="nav-btn">فردا →</a>'

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{word["word"]} — IELTS Word of the Day</title>
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
  max-width: 560px;
  width: 100%;
  box-shadow: 0 25px 50px rgba(0,0,0,.4);
}}
.badge {{
  display: inline-block;
  background: rgba(59,130,246,.15);
  color: var(--accent2);
  font-size: .75rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  padding: .35rem .75rem;
  border-radius: 999px;
  margin-bottom: 1.25rem;
}}
.word {{
  font-family: 'DM Serif Display', serif;
  font-size: 3rem;
  color: #fff;
  line-height: 1.1;
  margin-bottom: .25rem;
}}
.pos {{
  color: var(--muted);
  font-style: italic;
  font-size: .95rem;
  margin-bottom: 1.5rem;
}}
.definition {{
  font-size: 1.1rem;
  line-height: 1.65;
  margin-bottom: 1rem;
}}
.fa {{
  font-size: 1rem;
  color: var(--accent2);
  direction: rtl;
  text-align: right;
  margin-bottom: 1.5rem;
  padding: .75rem 1rem;
  background: rgba(59,130,246,.08);
  border-radius: 10px;
  border-right: 3px solid var(--accent);
}}
.examples-title {{
  font-size: .8rem;
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: .75rem;
}}
.examples {{
  list-style: none;
}}
.examples li {{
  padding: .65rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .95rem;
  line-height: 1.55;
  color: #cbd5e1;
}}
.examples li:last-child {{ border-bottom: none; }}
.meta {{
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: .75rem;
  font-size: .82rem;
  color: var(--muted);
}}
.nav {{ display: flex; gap: .5rem; }}
.nav-btn {{
  color: var(--accent2);
  text-decoration: none;
  padding: .4rem .75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: .82rem;
  transition: background .2s;
}}
.nav-btn:hover {{ background: rgba(59,130,246,.1); }}
footer {{
  text-align: center;
  margin-top: 1.5rem;
  font-size: .75rem;
  color: var(--muted);
}}
</style>
</head>
<body>
<div>
  <div class="card">
    <div class="badge">IELTS Essential Words · {day.strftime("%B %d, %Y")}</div>
    <h1 class="word">{word["word"]}</h1>
    <p class="pos">{pos}</p>
    <p class="definition">{word["definition"]}</p>
    {fa_block}
    <p class="examples-title">Examples</p>
    <ul class="examples">{ex_html}</ul>
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
        day = date.fromordinal(START.toordinal() + (date.today().toordinal() - START.toordinal()) + offset)
        word, num, total = word_for_offset((date.today().toordinal() - START.toordinal()) + offset)
        html = render_page(word, num, total, day, offset)
        return html.encode("utf-8")

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
