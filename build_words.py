#!/usr/bin/env python3
"""Build words.json from chapter data files."""

import json
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"


def parse_line(line: str) -> dict:
    parts = line.strip().split("|")
    if len(parts) != 6:
        raise ValueError(f"Bad line ({len(parts)} fields): {line[:80]}")
    word, pos, definition, fa, ex1, ex2 = parts
    return {
        "word": word,
        "pos": pos,
        "definition": definition,
        "fa": fa,
        "examples": [ex1, ex2],
    }


def main():
    words = []
    for i in range(1, 11):
        path = DATA / f"ch{i:02d}.txt"
        chapter = [parse_line(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(chapter) != 60:
            raise SystemExit(f"{path.name}: expected 60 words, got {len(chapter)}")
        words.extend(chapter)

    out = BASE / "words.json"
    out.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(words)} words to {out}")


if __name__ == "__main__":
    main()
