"""User authentication and sessions."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from db import connect, init_db, now_iso

TZ = ZoneInfo("Asia/Tehran")
SESSION_DAYS = 30
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _secret() -> bytes:
    from pathlib import Path
    path = Path(__file__).parent / "data" / ".secret"
    if path.exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    path.write_bytes(key)
    path.chmod(0o600)
    return key


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + ":" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        got = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return hmac.compare_digest(got, expected)
    except (ValueError, TypeError):
        return False


def validate_email(email: str) -> str | None:
    email = email.strip().lower()
    if not email or not EMAIL_RE.match(email):
        return "ایمیل معتبر وارد کنید"
    return None


def validate_password(password: str) -> str | None:
    if len(password) < 6:
        return "رمز عبور باید حداقل ۶ کاراکتر باشد"
    return None


def register_user(email: str, password: str) -> tuple[dict | None, str | None]:
    init_db()
    err = validate_email(email) or validate_password(password)
    if err:
        return None, err
    email = email.strip().lower()
    pw_hash = hash_password(password)
    try:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                (email, pw_hash, now_iso()),
            )
            user_id = cur.lastrowid
        return {"id": user_id, "email": email}, None
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return None, "این ایمیل قبلاً ثبت شده"
        return None, "خطا در ثبت‌نام"


def login_user(email: str, password: str) -> tuple[dict | None, str | None]:
    init_db()
    email = email.strip().lower()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        return None, "ایمیل یا رمز عبور اشتباه است"
    return {"id": row["id"], "email": row["email"]}, None


def create_session(user_id: int) -> dict:
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(16)
    expires = (datetime.now(TZ) + timedelta(days=SESSION_DAYS)).isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, csrf_token, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, csrf, expires),
        )
    return {"token": token, "csrf": csrf}


def delete_session(token: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def get_session_user(token: str | None) -> dict | None:
    if not token:
        return None
    init_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT s.token, s.csrf_token, s.expires_at, u.id, u.email
            FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
    if not row:
        return None
    expires = datetime.fromisoformat(row["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=TZ)
    if datetime.now(TZ) > expires:
        delete_session(token)
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "token": row["token"],
        "csrf": row["csrf_token"],
    }


def mark_word_read(user_id: int, word_index: int) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO read_words (user_id, word_index, read_at) VALUES (?, ?, ?)",
            (user_id, word_index, now_iso()),
        )


def get_read_indices(user_id: int) -> set[int]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT word_index FROM read_words WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    return {r["word_index"] for r in rows}


def count_read_words(user_id: int) -> int:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM read_words WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return row["c"] if row else 0
