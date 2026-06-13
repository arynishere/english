#!/usr/bin/env python3
"""Fetch and cache today's (or a given date's) word from online sources."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from fetcher import fetch_word

BASE = Path(__file__).parent
CACHE_DIR = BASE / "cache"
WORDS = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
START = date(2026, 1, 1)


def word_index_for(d: date) -> int:
    return (d.toordinal() - START.toordinal()) % len(WORDS)


def cache_path(d: date) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{d.isoformat()}.json"


def update_day(d: date | None = None, force: bool = False) -> Path:
    d = d or date.today()
    path = cache_path(d)
    if path.exists() and not force:
        print(f"[update] cache exists: {path}")
        return path

    idx = word_index_for(d)
    local = WORDS[idx]
    word = local["word"]
    print(f"[update] fetching '{word}' for {d.isoformat()}...")

    enriched = fetch_word(word, local)
    payload = {
        "date": d.isoformat(),
        "num": idx + 1,
        "total": len(WORDS),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        **enriched,
    }

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[update] saved {path} ({len(enriched.get('sources', []))} sources)")
    return path


def main():
    force = "--force" in sys.argv
    d = date.today()
    for arg in sys.argv[1:]:
        if arg.startswith("--date="):
            d = date.fromisoformat(arg.split("=", 1)[1])
    update_day(d, force=force)


if __name__ == "__main__":
    main()
