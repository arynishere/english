"""Web Push notifications — VAPID keys and daily reminders."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from db import connect, init_db, now_iso

BASE = Path(__file__).parent
VAPID_DIR = BASE / "data" / "vapid"
VAPID_EMAIL = "mailto:admin@english.v4vendetta.sbs"


def ensure_vapid() -> "object":
    from py_vapid import Vapid02

    VAPID_DIR.mkdir(parents=True, exist_ok=True)
    priv = VAPID_DIR / "private.pem"
    pub = VAPID_DIR / "public.pem"
    vapid = Vapid02()
    if priv.exists() and pub.exists():
        vapid.from_file(str(priv))
    else:
        vapid.generate_keys()
        priv.write_bytes(vapid.private_pem())
        pub.write_bytes(vapid.public_pem())
        priv.chmod(0o600)
    return vapid


def public_key_b64() -> str:
    """URL-safe base64 public key for browser PushManager."""
    from cryptography.hazmat.primitives import serialization

    vapid = ensure_vapid()
    raw = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def save_subscription(sub: dict, user_id: int | None = None) -> None:
    init_db()
    keys = sub.get("keys", {})
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO push_subscriptions (endpoint, p256dh, auth, user_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(endpoint) DO UPDATE SET
                p256dh = excluded.p256dh,
                auth = excluded.auth,
                user_id = excluded.user_id
            """,
            (
                sub["endpoint"],
                keys.get("p256dh", ""),
                keys.get("auth", ""),
                user_id,
                now_iso(),
            ),
        )


def get_all_subscriptions() -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT endpoint, p256dh, auth FROM push_subscriptions"
        ).fetchall()
    return [
        {
            "endpoint": r["endpoint"],
            "keys": {"p256dh": r["p256dh"], "auth": r["auth"]},
        }
        for r in rows
    ]


def send_push(subscription: dict, title: str, body: str, url: str = "/?tab=words") -> bool:
    from pywebpush import WebPushException, webpush

    vapid = ensure_vapid()
    payload = json.dumps({"title": title, "body": body, "url": url})
    try:
        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=vapid.private_pem(),
            vapid_claims={"sub": VAPID_EMAIL},
        )
        return True
    except WebPushException as exc:
        print(f"[push] failed: {exc}")
        if exc.response and exc.response.status_code in (404, 410):
            _remove_subscription(subscription["endpoint"])
        return False


def _remove_subscription(endpoint: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM push_subscriptions WHERE endpoint = ?", (endpoint,))


def send_daily_reminders() -> int:
    subs = get_all_subscriptions()
    if not subs:
        print("[push] no subscriptions")
        return 0
    title = "IELTS Daily · کلمات امروز"
    body = "کلمات امروزت رو یادت نره! بیا ۴ کلمه جدید یاد بگیر 📖"
    sent = sum(1 for s in subs if send_push(s, title, body))
    print(f"[push] sent {sent}/{len(subs)}")
    return sent
