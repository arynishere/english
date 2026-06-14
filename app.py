#!/usr/bin/env python3
"""Daily IELTS Essential Words — english.v4vendetta.sbs"""

import json
import mimetypes
import os
import threading
from datetime import date, datetime
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from zoneinfo import ZoneInfo

from auth import (
    create_session,
    delete_session,
    get_read_indices,
    get_session_user,
    login_user,
    mark_word_read,
    register_user,
)
from db import init_db
from push import public_key_b64, save_subscription
from update_daily import (
    TZ,
    WORDS_PER_DAY,
    cache_path,
    get_word_entry,
    update_day,
    word_indices_for,
)
from views import (
    render_books_tab,
    render_dictionaries_tab,
    render_login_page,
    render_register_page,
    render_words_tab,
    render_words_tab_user,
)

PORT = int(os.environ.get("PORT", "8092"))
BASE = Path(__file__).parent
STATIC = BASE / "static"
WORDS = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
START = date(2026, 1, 1)
_fetch_lock = threading.Lock()

init_db()

STATIC_ROUTES = {
    "/manifest.json": STATIC / "manifest.json",
    "/sw.js": STATIC / "sw.js",
    "/icons/logo.svg": STATIC / "icons" / "logo.svg",
    "/icons/icon-180.png": STATIC / "icons" / "icon-180.png",
    "/icons/icon-192.png": STATIC / "icons" / "icon-192.png",
    "/icons/icon-512.png": STATIC / "icons" / "icon-512.png",
}


def load_cached(d: date) -> dict | None:
    path = cache_path(d)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if "words" not in data and "word" in data:
        data = {
            "date": data.get("date", d.isoformat()),
            "words_per_day": 1,
            "day_num": data.get("num", 1),
            "total_days": len(WORDS),
            "total_words": len(WORDS),
            "fetched_at": data.get("fetched_at", ""),
            "words": [data],
        }
    return data


def get_day_data(d: date) -> dict:
    cached = load_cached(d)
    if cached:
        return cached

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

    entries = [get_word_entry(idx) for idx in word_indices_for(d)]
    total_days = (len(WORDS) + WORDS_PER_DAY - 1) // WORDS_PER_DAY
    return {
        "date": d.isoformat(),
        "words_per_day": WORDS_PER_DAY,
        "day_num": ((d.toordinal() - START.toordinal()) % total_days) + 1,
        "total_days": total_days,
        "total_words": len(WORDS),
        "fetched_at": datetime.now(TZ).isoformat(),
        "words": entries,
    }


def get_user_words(user_id: int) -> dict:
    read = get_read_indices(user_id)
    unread_indices = [i for i in range(len(WORDS)) if i not in read][:WORDS_PER_DAY]
    entries = [get_word_entry(i) for i in unread_indices]
    read_count = len(read)
    return {
        "words": entries,
        "read_count": read_count,
        "total_words": len(WORDS),
        "remaining": len(WORDS) - read_count,
        "fetched_at": datetime.now(TZ).isoformat(),
    }


def format_fetched_label(fetched: str) -> str:
    if not fetched:
        return "—"
    try:
        ts = datetime.fromisoformat(fetched.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=TZ)
        return ts.astimezone(TZ).strftime("%Y-%m-%d %H:%M") + " (Tehran)"
    except ValueError:
        return fetched[:16]


def parse_cookies(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    raw = handler.headers.get("Cookie", "")
    jar = cookies.SimpleCookie()
    jar.load(raw)
    return {k: jar[k].value for k in jar}


def parse_form(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length).decode("utf-8", errors="replace")
    return {k: v[0] for k, v in parse_qs(body).items()}


def parse_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length).decode("utf-8", errors="replace")
    return json.loads(body) if body else {}


def redirect(handler: BaseHTTPRequestHandler, location: str, clear_session: bool = False, session_token: str | None = None):
    handler.send_response(303)
    handler.send_header("Location", location)
    if clear_session:
        handler.send_header("Set-Cookie", "session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
    elif session_token:
        handler.send_header(
            "Set-Cookie",
            f"session={session_token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={30 * 86400}",
        )
    handler.end_headers()


class Handler(BaseHTTPRequestHandler):
    def _current_user(self) -> dict | None:
        return get_session_user(parse_cookies(self).get("session"))

    def _send_bytes(self, body: bytes, content_type: str, extra_headers: dict | None = None, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send_bytes(body, "application/json; charset=utf-8", status=status)

    def _serve_static(self, path: str) -> bool:
        file_path = STATIC_ROUTES.get(path)
        if not file_path or not file_path.is_file():
            return False
        body = file_path.read_bytes()
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        extra = {}
        if path == "/sw.js":
            ctype = "application/javascript; charset=utf-8"
            extra["Service-Worker-Allowed"] = "/"
            extra["Cache-Control"] = "no-cache"
        if path == "/manifest.json":
            ctype = "application/manifest+json; charset=utf-8"
        self._send_bytes(body, ctype, extra)
        return True

    def _build_page(self) -> bytes | None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)
        user = self._current_user()

        if path == "/login":
            return render_login_page(user, qs.get("error", [""])[0]).encode("utf-8")
        if path == "/register":
            return render_register_page(user, qs.get("error", [""])[0]).encode("utf-8")
        if path not in ("/", "/index.html"):
            return None

        tab = qs.get("tab", ["words"])[0]
        offset = int(qs.get("offset", ["0"])[0])

        if tab == "books":
            return render_books_tab(user).encode("utf-8")
        if tab == "dictionaries":
            return render_dictionaries_tab(user).encode("utf-8")

        if user:
            data = get_user_words(user["id"])
            fetched = format_fetched_label(data.get("fetched_at", ""))
            return render_words_tab_user(user, data, fetched).encode("utf-8")

        day = date.fromordinal(
            START.toordinal() + (date.today().toordinal() - START.toordinal()) + offset
        )
        data = get_day_data(day)
        fetched = format_fetched_label(data.get("fetched_at", ""))
        return render_words_tab(data, day, offset, fetched, user=None).encode("utf-8")

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"

        if path == "/api/vapid-public-key":
            self._send_json({"publicKey": public_key_b64()})
            return

        if self._serve_static(path):
            return

        body = self._build_page()
        if body is None:
            self.send_error(404)
            return
        self._send_bytes(body, "text/html; charset=utf-8")

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        user = self._current_user()

        if path == "/api/push/subscribe":
            try:
                sub = parse_json(self)
                save_subscription(sub, user["id"] if user else None)
                self._send_json({"ok": True})
            except (json.JSONDecodeError, KeyError) as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
            return

        form = parse_form(self)

        if path == "/register":
            u, err = register_user(form.get("email", ""), form.get("password", ""))
            if err:
                redirect(self, f"/register?error={quote(err)}")
                return
            sess = create_session(u["id"])
            redirect(self, "/?tab=words", session_token=sess["token"])
            return

        if path == "/login":
            u, err = login_user(form.get("email", ""), form.get("password", ""))
            if err:
                redirect(self, f"/login?error={quote(err)}")
                return
            sess = create_session(u["id"])
            redirect(self, "/?tab=words", session_token=sess["token"])
            return

        if path == "/logout":
            if user:
                delete_session(user["token"])
            redirect(self, "/?tab=words", clear_session=True)
            return

        if path == "/mark-read":
            if not user:
                redirect(self, "/login")
                return
            if form.get("csrf") != user["csrf"]:
                redirect(self, "/?tab=words&error=csrf")
                return
            try:
                word_index = int(form.get("word_index", "-1"))
            except ValueError:
                word_index = -1
            if 0 <= word_index < len(WORDS):
                mark_word_read(user["id"], word_index)
            redirect(self, "/?tab=words")
            return

        self.send_error(404)

    def do_HEAD(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/api/vapid-public-key":
            self._send_json({"publicKey": public_key_b64()})
            return
        if self._serve_static(path):
            return
        body = self._build_page()
        if body is None:
            self.send_error(404)
            return
        self._send_bytes(body, "text/html; charset=utf-8")

    def log_message(self, fmt, *args):
        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now} Tehran] {args[0]}")


def main():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"IELTS Daily Words running on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
