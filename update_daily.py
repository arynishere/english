#!/usr/bin/env python3
"""Fetch and cache today's words from online sources."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fetcher import fetch_word

BASE = Path(__file__).parent
CACHE_DIR = BASE / "cache"
WORDS = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
START = date(2026, 1, 1)
TZ = ZoneInfo("Asia/Tehran")
WORDS_PER_DAY = 4


def day_index(d: date) -> int:
    return d.toordinal() - START.toordinal()


def word_indices_for(d: date) -> list[int]:
    base = day_index(d) * WORDS_PER_DAY
    return [(base + i) % len(WORDS) for i in range(WORDS_PER_DAY)]


def word_index_for(d: date) -> int:
    """First word index of the day (backward compatibility)."""
    return word_indices_for(d)[0]


def cache_path(d: date) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{d.isoformat()}.json"


def fetch_word_entry(idx: int) -> dict:
    local = WORDS[idx]
    enriched = fetch_word(local["word"], local)
    return {"num": idx + 1, "word_index": idx, **enriched}


def word_cache_path(idx: int) -> Path:
    return CACHE_DIR / "words" / f"{idx:04d}.json"


def get_word_entry(idx: int) -> dict:
    wp = word_cache_path(idx)
    if wp.exists():
        try:
            return json.loads(wp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    entry = fetch_word_entry(idx)
    wp.parent.mkdir(parents=True, exist_ok=True)
    wp.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    return entry


def update_day(d: date | None = None, force: bool = False) -> Path:
    d = d or date.today()
    path = cache_path(d)
    if path.exists() and not force:
        print(f"[update] cache exists: {path}")
        return path

    indices = word_indices_for(d)
    names = [WORDS[i]["word"] for i in indices]
    print(f"[update] fetching {len(indices)} words for {d.isoformat()}: {', '.join(names)}")

    entries = []
    for idx in indices:
        entries.append(get_word_entry(idx))

    total_days = (len(WORDS) + WORDS_PER_DAY - 1) // WORDS_PER_DAY
    payload = {
        "date": d.isoformat(),
        "words_per_day": WORDS_PER_DAY,
        "day_num": (day_index(d) % total_days) + 1,
        "total_days": total_days,
        "total_words": len(WORDS),
        "fetched_at": datetime.now(TZ).isoformat(),
        "words": entries,
    }

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[update] saved {path} ({len(entries)} words)")
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
