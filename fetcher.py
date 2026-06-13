#!/usr/bin/env python3
"""Fetch word definitions and examples from online dictionary sources."""

from __future__ import annotations

import html as htmlmod
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

USER_AGENT = "Mozilla/5.0 (compatible; IELTSDailyWord/1.0; +https://english.v4vendetta.sbs)"
TIMEOUT = 15


@dataclass
class SourceResult:
    name: str
    url: str
    definition: str = ""
    pos: str = ""
    examples: list[str] = field(default_factory=list)
    phonetic: str = ""
    ok: bool = False


def _get(url: str, accept: str = "text/html") -> str | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"[fetcher] {url}: {exc}")
        return None


def _get_json(url: str) -> object | None:
    body = _get(url, accept="application/json")
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fetch_cambridge(word: str) -> SourceResult:
    url = f"https://dictionary.cambridge.org/dictionary/english/{word.lower()}"
    result = SourceResult(name="Cambridge Dictionary", url=url)
    page = _get(url)
    if not page:
        return result

    pos_match = re.search(r'class="pos dpos"[^>]*>.*?<span[^>]*>([^<]+)', page, re.DOTALL)
    if pos_match:
        result.pos = htmlmod.unescape(pos_match.group(1).strip())

    defs = [
        htmlmod.unescape(m.group(1).strip().rstrip(":"))
        for m in re.finditer(r'class="def ddef_d db">([^<]+)', page)
    ]
    defs = [d for d in defs if d]
    if defs:
        result.definition = defs[0]

    for block in re.findall(r'class="eg deg">(.*?)</div>', page, re.DOTALL):
        text = re.sub(r"<[^>]+>", "", block)
        text = htmlmod.unescape(text).strip()
        if text and len(text) > 8:
            result.examples.append(text)

    phon = re.search(r'class="ipa dipa[^"]*">([^<]+)', page)
    if phon:
        result.phonetic = htmlmod.unescape(phon.group(1).strip())

    result.ok = bool(result.definition or result.examples)
    return result


def fetch_wiktionary(word: str) -> SourceResult:
    url = f"https://en.wiktionary.org/wiki/{word.lower()}"
    api_url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word.lower()}"
    result = SourceResult(name="Wiktionary", url=url)
    data = _get_json(api_url)
    if not isinstance(data, dict) or "en" not in data:
        return result

    entry = data["en"][0]
    result.pos = entry.get("partOfSpeech", "")

    definitions = entry.get("definitions", [])
    if definitions:
        defn = definitions[0].get("definition", "")
        defn = re.sub(r"<[^>]+>", "", defn)
        result.definition = htmlmod.unescape(defn).strip()

    for item in definitions:
        for ex in item.get("examples", []):
            ex = re.sub(r"<[^>]+>", "", ex)
            ex = htmlmod.unescape(ex).strip()
            if ex and len(ex) > 8:
                result.examples.append(ex)

    result.examples = list(dict.fromkeys(result.examples))[:4]
    result.ok = bool(result.definition or result.examples)
    return result


def fetch_free_dictionary(word: str) -> SourceResult:
    url = f"https://dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
    result = SourceResult(name="Free Dictionary API", url="https://dictionaryapi.dev/")
    data = _get_json(url)
    if not isinstance(data, list) or not data:
        return result

    entry = data[0]
    result.phonetic = entry.get("phonetic", "")

    for meaning in entry.get("meanings", []):
        if not result.pos:
            result.pos = meaning.get("partOfSpeech", "")
        for defn in meaning.get("definitions", []):
            if not result.definition and defn.get("definition"):
                result.definition = defn["definition"]
            if defn.get("example"):
                ex = defn["example"].strip()
                if len(ex) > 8:
                    result.examples.append(ex)
            if result.definition and len(result.examples) >= 3:
                break
        if result.definition and len(result.examples) >= 3:
            break

    result.examples = list(dict.fromkeys(result.examples))[:4]
    result.ok = bool(result.definition or result.examples)
    return result


def merge_results(word: str, local: dict, results: list[SourceResult]) -> dict:
    """Merge online sources; keep Persian translation from local list."""
    active = [r for r in results if r.ok]
    definition = ""
    pos = local.get("pos", "")
    phonetic = ""
    examples: list[dict] = []
    seen_ex: set[str] = set()

    for src in active:
        if not definition and src.definition:
            definition = src.definition
        if not pos and src.pos:
            pos = src.pos
        if not phonetic and src.phonetic:
            phonetic = src.phonetic
        for ex in src.examples:
            key = ex.lower()
            if key not in seen_ex:
                seen_ex.add(key)
                examples.append({"text": ex, "source": src.name})

    if not definition:
        definition = local.get("definition", "")
    if not examples:
        examples = [{"text": ex, "source": "IELTS Essential Words (local)"} for ex in local.get("examples", [])]

    sources = [{"name": r.name, "url": r.url} for r in active]
    if not sources:
        sources = [{"name": "IELTS Essential Words (local)", "url": "https://github.com/arynishere/english"}]

    return {
        "word": word,
        "pos": pos,
        "definition": definition,
        "fa": local.get("fa", ""),
        "phonetic": phonetic,
        "examples": examples[:4],
        "sources": sources,
        "online": bool(active),
    }


def fetch_word(word: str, local: dict) -> dict:
    results = [
        fetch_cambridge(word),
        fetch_wiktionary(word),
        fetch_free_dictionary(word),
    ]
    return merge_results(word, local, results)
