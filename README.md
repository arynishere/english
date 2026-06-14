# IELTS Daily

A daily IELTS vocabulary app — **4 words per day** with English definitions, Persian translations, pronunciation, and example sentences fetched from online dictionaries.

**Live:** [https://english.v4vendetta.sbs](https://english.v4vendetta.sbs)

## Features

### Vocabulary
- **600 words** from the IELTS Essential Words list
- **4 words per day** — calendar-based rotation from `2026-01-01` (150-day full cycle)
- **Live definitions & examples** fetched daily from:
  - [Cambridge Dictionary](https://dictionary.cambridge.org/)
  - [Wiktionary](https://en.wiktionary.org/)
  - [Free Dictionary API](https://dictionaryapi.dev/) (when available)
- **Source attribution** on each example and in the page footer
- **Pronunciation** — American 🇺🇸 and British 🇬🇧 (Cambridge/Wiktionary audio + browser speech fallback)
- Persian translation from the local IELTS word list

### UI & UX
- Dark modern theme with **Vazirmatn** (Persian) and **Inter** (English)
- **3 tabs:** Daily Words · Books · Dictionaries
- Browse previous / next sets with `/?tab=words&offset=-1`
- **iOS safe-area** support (notch / Dynamic Island)

### Accounts
- Register / login with email and password
- Mark words as **read** — they never appear again for logged-in users
- Progress tracking (read count / 600)

### PWA & Push Notifications
- Install as a **Progressive Web App** on mobile (Add to Home Screen)
- Custom app icon — open book with a green **4** badge
- **Daily push reminder at 10:00 Asia/Tehran** — *"کلمات امروزت رو یادت نره!"*
- Service worker for offline shell caching

## Project structure

```
english/
├── app.py              # HTTP server, routing, auth, static, push API
├── views.py            # HTML/CSS templates (tabs, cards, PWA banner)
├── auth.py             # Registration, login, sessions
├── db.py               # SQLite — users, read words, push subscriptions
├── push.py             # VAPID keys + Web Push delivery
├── send_push.py        # Daily reminder script (systemd)
├── fetcher.py          # Cambridge, Wiktionary, Free Dictionary API
├── update_daily.py     # Daily fetch + cache
├── generate_icons.py   # Regenerate PWA icons (180/192/512)
├── resources.json      # Books & dictionary links
├── words.json          # 600-word vocabulary (generated)
├── build_words.py      # Rebuild words.json from data/ch*.txt
├── requirements.txt    # pywebpush, py-vapid, Pillow
├── static/
│   ├── manifest.json   # PWA manifest
│   ├── sw.js           # Service worker
│   └── icons/          # logo.svg, icon-180/192/512.png
├── cache/              # Daily cached word JSON (gitignored)
├── data/
│   ├── ch01.txt … ch10.txt   # 60 words per chapter (pipe-delimited)
│   ├── app.db          # SQLite database (gitignored)
│   └── vapid/          # VAPID keys (gitignored)
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

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
# → http://127.0.0.1:8092
```

Optional port:

```bash
PORT=3000 python3 app.py
```

VAPID keys for push notifications are auto-generated on first run in `data/vapid/`.

## Rebuild `words.json`

After editing chapter files in `data/`:

```bash
python3 build_words.py
```

Each chapter file must contain exactly **60 words** (10 chapters × 60 = 600 total).

## Regenerate PWA icons

```bash
python3 generate_icons.py
```

Outputs `static/icons/icon-180.png`, `icon-192.png`, and `icon-512.png`.

## Daily online update

```bash
# Fetch today's words manually
python3 update_daily.py

# Force re-fetch (ignore cache)
python3 update_daily.py --force

# Fetch a specific date
python3 update_daily.py --date=2026-06-14
```

Cached data is stored in `cache/YYYY-MM-DD.json` and includes source URLs.

### systemd timers (production)

| Timer | Schedule | Purpose |
|-------|----------|---------|
| `english-daily-update.timer` | 00:05 Asia/Tehran | Fetch daily word definitions |
| `english-daily-push.timer` | 10:00 Asia/Tehran | Send push reminders to subscribers |

```bash
systemctl enable --now english-daily.service
systemctl enable --now english-daily-update.timer
systemctl enable --now english-daily-push.timer
```

Manual push test:

```bash
python3 send_push.py
```

## Deploy (nginx + systemd)

1. Copy the project to the server (e.g. `/root/english`)
2. Create a virtualenv and install dependencies
3. Create a systemd service pointing to `venv/bin/python3 app.py` on port `8092`
4. Add an nginx site block proxying to `127.0.0.1:8092`
5. Run `./setup-ssl.sh` or `certbot --nginx -d your.domain`

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

HTTPS is required for service workers and push notifications.

## How daily words work

Words are selected in groups of **4 per day** by day index, starting from `2026-01-01`:

```python
base = (today - start_date).days * 4
words = [word_list[(base + i) % 600] for i in range(4)]
```

For **logged-in users**, the app shows the next 4 unread words instead of the calendar rotation.

Definitions and examples are fetched live from online dictionaries and cached for that day. If the network is unavailable, the app falls back to the local `words.json` entry.

## PWA install (mobile)

1. Open [english.v4vendetta.sbs](https://english.v4vendetta.sbs) in Chrome (Android) or Safari (iOS)
2. **Android:** tap *Install app* in the banner, or Menu → Add to Home Screen
3. **iOS:** Share → Add to Home Screen
4. Tap **فعال‌سازی یادآوری ۱۰ صبح** to enable daily push notifications

> On iOS, push notifications work when the app is installed to the Home Screen and notification permission is granted.

## License

MIT — use freely for learning and personal projects.
