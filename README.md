# IELTS Daily Word

A minimal daily vocabulary app that teaches one **IELTS Essential Word** per day with English definition, Persian translation, and example sentences.

**Live:** [https://english.v4vendetta.sbs](https://english.v4vendetta.sbs)

## Features

- **600 words** from the IELTS Essential Words list
- **One word per day** — deterministic rotation based on the calendar date
- Each entry includes:
  - Part of speech
  - English definition
  - Persian translation (`fa`)
  - Two example sentences
- Browse previous / next words with `/?offset=-1` and `/?offset=1`
- Lightweight Python server (stdlib only, no dependencies)
- Nginx reverse proxy + Let's Encrypt SSL

## Project structure

```
english/
├── app.py              # Web server
├── words.json          # 600-word vocabulary (generated)
├── build_words.py      # Rebuild words.json from data/ch*.txt
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

Everyone sees the same word on the same calendar day.

## License

MIT — use freely for learning and personal projects.
