# IELTS Daily Word

A minimal daily vocabulary app that teaches one **IELTS Essential Word** per day with English definition, Persian translation, and example sentences.

**Live:** [https://english.v4vendetta.sbs](https://english.v4vendetta.sbs)

## Features

- **600 words** from the IELTS Essential Words list
- **One word per day** — deterministic rotation based on the calendar date
- **Live definitions & examples** fetched daily from online dictionaries:
  - [Cambridge Dictionary](https://dictionary.cambridge.org/)
  - [Wiktionary](https://en.wiktionary.org/)
  - [Free Dictionary API](https://dictionaryapi.dev/) (when available)
- **Source attribution** — each example and the page footer show where data came from
- Persian translation kept from the local IELTS word list
- Automatic daily refresh via systemd timer (00:05 UTC)
- Browse previous / next words with `/?offset=-1` and `/?offset=1`
- Lightweight Python server (stdlib only, no dependencies)
- Nginx reverse proxy + Let's Encrypt SSL

## Project structure

```
english/
├── app.py              # Web server
├── fetcher.py          # Fetch from Cambridge, Wiktionary, Free Dictionary API
├── update_daily.py     # Daily fetch + cache script
├── words.json          # 600-word vocabulary (generated)
├── build_words.py      # Rebuild words.json from data/ch*.txt
├── cache/              # Daily cached word JSON (gitignored)
├── data/
│   ├── ch01.txt … ch10.txt   # 60 words per chapter (pipe-delimited)
├── setup-ssl.sh        # Certbot helper for nginx
└── README.md
```

### Word data format (`data/ch01.txt`)

Each line is pipe-delimited:

```
word|pos|definition|persian_translation|example_1|example_2
```

Example:

```
abundant|adj.|existing in large quantities; plentiful|فراوان، زیاد|The region has abundant natural resources.|Fish are abundant in this lake during spring.
```

## Run locally

```bash
python3 app.py
# → http://127.0.0.1:8092
```

Optional port:

```bash
PORT=3000 python3 app.py
```

## Rebuild `words.json`

After editing chapter files in `data/`:

```bash
python3 build_words.py
```

Each chapter file must contain exactly **60 words** (10 chapters × 60 = 600 total).

## Daily online update

The app fetches fresh definitions and examples every day:

```bash
# Fetch today's word manually
python3 update_daily.py

# Force re-fetch (ignore cache)
python3 update_daily.py --force

# Fetch a specific date
python3 update_daily.py --date=2026-06-14
```

Cached data is stored in `cache/YYYY-MM-DD.json` and includes source URLs.

### systemd timer (production)

```bash
systemctl enable --now english-daily-update.timer
```

Runs daily at **00:05 UTC** with a small random delay.

## Deploy (nginx + systemd)

1. Copy the project to the server (e.g. `/root/english`)
2. Create a systemd service pointing to `app.py` on port `8092`
3. Add an nginx site block proxying to `127.0.0.1:8092`
4. Run `./setup-ssl.sh` or `certbot --nginx -d your.domain`

Example nginx location block:

```nginx
location / {
    proxy_pass http://127.0.0.1:8092;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## How "word of the day" works

Words are selected by day index modulo 600, starting from `2026-01-01`:

```python
idx = (today - start_date).days % 600
word = words[idx]
```

Definitions and examples are then fetched live from online dictionaries and cached for that day. If the network is unavailable, the app falls back to the local `words.json` entry.

## License

MIT — use freely for learning and personal projects.
