"""HTML views for IELTS Daily Words app."""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
RESOURCES = json.loads((BASE / "resources.json").read_text(encoding="utf-8"))

TABS = [
    ("words", "کلمات روز", "Daily Words", "📖"),
    ("books", "کتاب‌ها", "Books", "📚"),
    ("dictionaries", "دیکشنری", "Dictionaries", "📕"),
]

CSS = """
:root {
  --bg: #080c10;
  --bg2: #0d1219;
  --surface: #141c27;
  --surface2: #1a2433;
  --border: rgba(148,163,184,.12);
  --border2: rgba(148,163,184,.2);
  --text: #e8edf4;
  --muted: #8b9cb3;
  --accent: #4f8cff;
  --accent2: #7ab4ff;
  --green: #3dd68c;
  --orange: #ffb347;
  --purple: #a78bfa;
  --font-fa: 'Vazirmatn', 'Tahoma', 'Arial', sans-serif;
  --font-en: 'Inter', system-ui, sans-serif;
  --font-display: 'DM Serif Display', Georgia, serif;
  --radius: 16px;
  --shadow: 0 8px 32px rgba(0,0,0,.35);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font-fa);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
body::before {
  content: '';
  position: fixed; inset: 0; z-index: -1;
  background:
    radial-gradient(ellipse 80% 50% at 10% -10%, rgba(79,140,255,.18), transparent),
    radial-gradient(ellipse 60% 40% at 90% 0%, rgba(167,139,250,.1), transparent),
    radial-gradient(ellipse 50% 30% at 50% 100%, rgba(61,214,140,.06), transparent);
}
a { color: var(--accent2); text-decoration: none; }
a:hover { text-decoration: underline; }

.app-shell { max-width: 760px; margin: 0 auto; padding: 0 1rem 5rem; }

/* ── Top bar ── */
.topbar {
  position: sticky; top: 0; z-index: 100;
  background: rgba(8,12,16,.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: .85rem 0 .75rem;
  margin-bottom: 1.5rem;
}
.topbar-inner { max-width: 760px; margin: 0 auto; padding: 0 1rem; }
.brand { display: flex; align-items: center; gap: .65rem; margin-bottom: .85rem; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; flex-shrink: 0;
}
.brand-text h1 {
  font-family: var(--font-fa);
  font-size: 1.15rem; font-weight: 700; color: #fff; line-height: 1.2;
}
.brand-text p { font-size: .72rem; color: var(--muted); font-family: var(--font-fa); }

/* ── Tabs ── */
.tabs {
  display: flex; gap: .35rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: .3rem;
}
.tab {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  gap: .1rem; padding: .55rem .4rem; border-radius: 9px;
  font-size: .72rem; font-weight: 500; color: var(--muted);
  text-decoration: none !important; transition: all .2s;
  text-align: center; line-height: 1.2;
}
.tab-icon { font-size: 1.1rem; }
.tab-en { font-size: .62rem; opacity: .75; font-family: var(--font-en); }
.tab:hover { color: var(--text); background: rgba(255,255,255,.04); text-decoration: none !important; }
.tab.active {
  background: linear-gradient(135deg, rgba(79,140,255,.25), rgba(167,139,250,.15));
  color: #fff; border: 1px solid rgba(79,140,255,.3);
  box-shadow: 0 2px 12px rgba(79,140,255,.15);
}

/* ── Page header ── */
.page-header { margin-bottom: 1.25rem; }
.page-title {
  font-family: var(--font-fa);
  font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: .35rem;
}
.page-sub { font-size: .85rem; color: var(--muted); font-family: var(--font-fa); }
.badges { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .65rem; }
.badge {
  font-size: .68rem; font-weight: 600; letter-spacing: .04em;
  text-transform: uppercase; padding: .28rem .65rem; border-radius: 999px;
  background: rgba(79,140,255,.12); color: var(--accent2);
  border: 1px solid rgba(79,140,255,.2);
}
.badge.live { background: rgba(61,214,140,.1); color: var(--green); border-color: rgba(61,214,140,.25); }

/* ── Word cards ── */
.word-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: .85rem;
  box-shadow: var(--shadow);
  transition: border-color .2s, transform .2s;
  animation: fadeUp .4s ease both;
}
.word-card:hover { border-color: var(--border2); }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.word-card:nth-child(1) { animation-delay: .05s; }
.word-card:nth-child(2) { animation-delay: .1s; }
.word-card:nth-child(3) { animation-delay: .15s; }
.word-card:nth-child(4) { animation-delay: .2s; }

.word-top { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; margin-bottom: .65rem; }
.word-left { flex: 1; min-width: 0; }
.word-num {
  display: inline-block; font-size: .68rem; font-weight: 700;
  color: var(--accent2); background: rgba(79,140,255,.1);
  padding: .15rem .5rem; border-radius: 5px; margin-bottom: .35rem;
}
.word-title {
  font-family: var(--font-display);
  font-size: 1.85rem; color: #fff; line-height: 1.15; word-break: break-word;
}
.pos { color: var(--muted); font-style: italic; font-size: .85rem; margin-top: .2rem; font-family: var(--font-en); }

.speak-group { display: flex; gap: .35rem; flex-shrink: 0; }
.speak-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--accent2); cursor: pointer; transition: all .2s;
  title: attr(data-label);
}
.speak-btn:hover { background: rgba(79,140,255,.15); border-color: rgba(79,140,255,.3); transform: scale(1.05); }
.speak-btn svg { width: 16px; height: 16px; }

.section-label {
  font-size: .68rem; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: .85rem 0 .35rem;
  font-family: var(--font-en);
}
.definition { font-size: .98rem; line-height: 1.75; color: var(--text); font-family: var(--font-en); }
.fa {
  direction: rtl; text-align: right;
  font-family: var(--font-fa);
  font-size: 1rem; font-weight: 500; color: var(--accent2);
  background: rgba(79,140,255,.07);
  border-right: 3px solid var(--accent);
  padding: .75rem 1rem; border-radius: 0 10px 10px 0;
  margin: .65rem 0; line-height: 1.85;
}

.examples { list-style: none; }
.examples li {
  padding: .6rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .88rem;
}
.examples li:last-child { border-bottom: none; }
.ex-text { color: #c8d5e8; display: block; line-height: 1.65; margin-bottom: .2rem; font-family: var(--font-en); }
.ex-src { font-size: .72rem; color: var(--muted); }

.word-sources { margin-top: .75rem; display: flex; flex-wrap: wrap; gap: .3rem; }
.src-tag {
  font-size: .68rem; color: var(--muted);
  padding: .2rem .55rem; border-radius: 999px;
  border: 1px solid var(--border); text-decoration: none !important;
  transition: all .15s;
}
.src-tag:hover { color: var(--accent2); border-color: rgba(79,140,255,.3); background: rgba(79,140,255,.08); text-decoration: none !important; }

/* ── Footer card ── */
.footer-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.1rem 1.4rem; margin-top: .5rem;
}
.progress-wrap { margin-bottom: .85rem; }
.progress-label { display: flex; justify-content: space-between; font-size: .75rem; color: var(--muted); margin-bottom: .35rem; }
.progress-bar { height: 4px; background: var(--surface2); border-radius: 99px; overflow: hidden; }
.progress-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--accent), var(--purple));
  transition: width .6s ease;
}
.meta { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .65rem; font-size: .8rem; color: var(--muted); }
.nav-btns { display: flex; gap: .4rem; }
.nav-btn {
  color: var(--accent2); padding: .4rem .85rem;
  border: 1px solid var(--border); border-radius: 9px;
  font-size: .8rem; text-decoration: none !important;
  transition: background .15s;
}
.nav-btn:hover { background: rgba(79,140,255,.1); text-decoration: none !important; }
.updated { font-size: .7rem; color: var(--muted); text-align: center; margin-top: .65rem; }

/* ── Resource cards (books & dicts) ── */
.resource-grid { display: flex; flex-direction: column; gap: .75rem; }
.resource-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.25rem 1.4rem;
  display: flex; gap: 1rem; align-items: flex-start;
  transition: border-color .2s, transform .2s;
  animation: fadeUp .35s ease both;
}
.resource-card:hover { border-color: var(--border2); transform: translateY(-2px); }
.resource-card:nth-child(n) { animation-delay: calc(var(--i, 0) * .05s); }

.resource-icon {
  width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
}
.icon-book { background: rgba(255,179,71,.12); }
.icon-dict-en { background: rgba(79,140,255,.12); }
.icon-dict-fa { background: rgba(61,214,140,.12); }

.resource-body { flex: 1; min-width: 0; }
.resource-top { display: flex; align-items: flex-start; justify-content: space-between; gap: .5rem; flex-wrap: wrap; margin-bottom: .3rem; }
.resource-name {
  font-family: var(--font-en);
  font-size: 1.05rem; color: #fff; line-height: 1.3;
}
.resource-badge {
  font-size: .62rem; font-weight: 700; letter-spacing: .04em;
  padding: .2rem .55rem; border-radius: 999px; white-space: nowrap;
  background: rgba(79,140,255,.12); color: var(--accent2);
  border: 1px solid rgba(79,140,255,.2);
}
.resource-badge.free { background: rgba(61,214,140,.1); color: var(--green); border-color: rgba(61,214,140,.25); }
.resource-badge.fa { background: rgba(61,214,140,.1); color: var(--green); border-color: rgba(61,214,140,.25); }
.resource-author { font-size: .78rem; color: var(--muted); margin-bottom: .35rem; }
.resource-desc { font-size: .84rem; color: #a8b8cc; line-height: 1.65; margin-bottom: .65rem; font-family: var(--font-fa); }
.resource-tags { display: flex; flex-wrap: wrap; gap: .3rem; margin-bottom: .65rem; }
.rtag {
  font-size: .65rem; padding: .15rem .45rem; border-radius: 5px;
  background: var(--surface2); color: var(--muted); border: 1px solid var(--border);
}
.resource-link {
  display: inline-flex; align-items: center; gap: .35rem;
  font-size: .8rem; font-weight: 600; color: var(--accent2) !important;
  padding: .45rem .9rem; border-radius: 8px;
  background: rgba(79,140,255,.1); border: 1px solid rgba(79,140,255,.2);
  text-decoration: none !important; transition: all .15s;
}
.resource-link:hover { background: rgba(79,140,255,.2); text-decoration: none !important; }

.section-divider {
  display: flex; align-items: center; gap: .75rem;
  margin: 1.5rem 0 1rem; font-size: .75rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
  font-family: var(--font-fa);
}
.section-divider::before, .section-divider::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

.site-footer {
  text-align: center; margin-top: 2rem;
  font-size: .72rem; color: var(--muted);
}

/* ── Auth bar ── */
.auth-bar {
  display: flex; align-items: center; justify-content: space-between;
  gap: .65rem; flex-wrap: wrap;
  margin-bottom: .75rem; padding: .55rem .75rem;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 10px; font-size: .78rem;
}
.auth-user { color: var(--text); }
.auth-user strong { color: #fff; }
.auth-progress { color: var(--green); font-weight: 600; }
.auth-links { display: flex; gap: .4rem; flex-wrap: wrap; }
.auth-link {
  color: var(--accent2) !important; text-decoration: none !important;
  padding: .3rem .65rem; border: 1px solid var(--border); border-radius: 7px;
  font-size: .75rem; transition: background .15s;
}
.auth-link:hover { background: rgba(79,140,255,.1); text-decoration: none !important; }
.auth-link.primary { background: rgba(79,140,255,.15); border-color: rgba(79,140,255,.3); }
.auth-link.danger { color: #f87171 !important; }

/* ── Auth forms ── */
.auth-card {
  max-width: 420px; margin: 2rem auto;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 2rem;
  box-shadow: var(--shadow);
}
.auth-card h2 {
  font-family: var(--font-fa);
  font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .35rem; text-align: center;
}
.auth-sub { text-align: center; color: var(--muted); font-size: .88rem; margin-bottom: 1.5rem; font-family: var(--font-fa); line-height: 1.75; }
.form-group { margin-bottom: 1rem; }
.form-group label {
  display: block; font-size: .78rem; font-weight: 600;
  color: var(--muted); margin-bottom: .35rem; font-family: var(--font-fa);
}
.form-input {
  width: 100%; padding: .7rem .9rem; border-radius: 10px;
  border: 1px solid var(--border); background: var(--surface2);
  color: var(--text); font-size: .92rem; font-family: var(--font-fa);
  transition: border-color .2s;
}
.form-input:focus { outline: none; border-color: var(--accent); }
.form-error {
  background: rgba(248,113,113,.1); border: 1px solid rgba(248,113,113,.3);
  color: #fca5a5; padding: .65rem .85rem; border-radius: 8px;
  font-size: .85rem; margin-bottom: 1rem; text-align: center;
  font-family: var(--font-fa); line-height: 1.65;
}
.btn-submit {
  width: 100%; padding: .75rem; border: none; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  color: #fff; font-size: .95rem; font-weight: 600; cursor: pointer;
  font-family: var(--font-fa);
  transition: opacity .2s, transform .15s;
}
.btn-submit:hover { opacity: .92; transform: translateY(-1px); }
.auth-switch {
  text-align: center; margin-top: 1.25rem; font-size: .85rem; color: var(--muted);
  font-family: var(--font-fa); line-height: 1.75;
}

/* ── Mark read ── */
.mark-form { margin-top: 1rem; }
.mark-btn {
  display: inline-flex; align-items: center; gap: .4rem;
  width: 100%; justify-content: center;
  padding: .7rem 1rem; border-radius: 10px;
  background: rgba(61,214,140,.1); border: 1px solid rgba(61,214,140,.3);
  color: var(--green); font-size: .88rem; font-weight: 600;
  font-family: var(--font-fa);
  cursor: pointer; transition: all .2s;
}
.mark-btn:hover { background: rgba(61,214,140,.18); transform: translateY(-1px); }

.empty-state {
  text-align: center; padding: 3rem 1.5rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius);
}
.empty-state h3 { font-family: var(--font-fa); font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: .5rem; }
.empty-state p { color: var(--muted); font-size: .92rem; font-family: var(--font-fa); line-height: 1.75; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.site-footer { font-family: var(--font-fa); }
.auth-bar, .auth-user, .auth-link, .nav-btn, .tab { font-family: var(--font-fa); }
.resource-link { font-family: var(--font-fa); }

/* ── PWA install banner ── */
.pwa-banner {
  display: none; align-items: center; justify-content: space-between; gap: .75rem;
  flex-wrap: wrap; margin-bottom: .85rem; padding: .75rem 1rem;
  background: linear-gradient(135deg, rgba(79,140,255,.15), rgba(167,139,250,.1));
  border: 1px solid rgba(79,140,255,.25); border-radius: 12px;
  font-family: var(--font-fa); font-size: .82rem;
}
.pwa-banner.show { display: flex; }
.pwa-banner-text { color: var(--text); line-height: 1.5; flex: 1; min-width: 180px; }
.pwa-actions { display: flex; gap: .4rem; flex-wrap: wrap; }
.pwa-btn {
  padding: .45rem .85rem; border-radius: 8px; font-size: .78rem; font-weight: 600;
  font-family: var(--font-fa); cursor: pointer; border: none; transition: all .15s;
}
.pwa-btn.primary { background: var(--accent); color: #fff; }
.pwa-btn.secondary { background: var(--surface2); color: var(--accent2); border: 1px solid var(--border); }
.pwa-btn.success { background: rgba(61,214,140,.15); color: var(--green); border: 1px solid rgba(61,214,140,.3); }
.pwa-btn:hover { opacity: .9; transform: translateY(-1px); }

@media (max-width: 480px) {
  .word-title { font-size: 1.55rem; }
  .page-title { font-size: 1.25rem; }
  .tab { font-size: .65rem; padding: .5rem .25rem; }
  .resource-card { flex-direction: column; gap: .65rem; }
}
"""

SPEAKER_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.06c1.48-.74 2.5-2.26 2.5-4.03zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>'

PWA_JS = """
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)));
}
async function subscribePush() {
  if (!('PushManager' in window)) { alert('مرورگر push notification رو پشتیبانی نمی‌کنه'); return; }
  const perm = await Notification.requestPermission();
  if (perm !== 'granted') return;
  const reg = await navigator.serviceWorker.ready;
  const { publicKey } = await fetch('/api/vapid-public-key').then(r => r.json());
  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicKey),
  });
  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sub.toJSON()),
  });
  localStorage.setItem('push-enabled', '1');
  updatePwaBanner();
}
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  updatePwaBanner();
});
function installPwa() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  deferredPrompt.userChoice.then(() => { deferredPrompt = null; updatePwaBanner(); });
}
function updatePwaBanner() {
  const banner = document.getElementById('pwaBanner');
  if (!banner) return;
  const pushOn = localStorage.getItem('push-enabled') === '1' || Notification.permission === 'granted';
  const installBtn = document.getElementById('pwaInstall');
  const pushBtn = document.getElementById('pwaPush');
  if (installBtn) installBtn.style.display = deferredPrompt ? 'inline-block' : 'none';
  if (pushBtn) {
    pushBtn.textContent = pushOn ? '🔔 یادآوری فعاله' : '🔔 فعال‌سازی یادآوری ۱۰ صبح';
    pushBtn.className = pushOn ? 'pwa-btn success' : 'pwa-btn primary';
    pushBtn.disabled = pushOn;
  }
  const show = deferredPrompt || !pushOn;
  banner.classList.toggle('show', show);
  if (localStorage.getItem('pwa-dismiss') === '1' && pushOn && !deferredPrompt) banner.classList.remove('show');
}
document.addEventListener('DOMContentLoaded', () => {
  updatePwaBanner();
  document.getElementById('pwaDismiss')?.addEventListener('click', () => {
    localStorage.setItem('pwa-dismiss', '1');
    document.getElementById('pwaBanner')?.classList.remove('show');
  });
  document.getElementById('pwaPush')?.addEventListener('click', subscribePush);
  document.getElementById('pwaInstall')?.addEventListener('click', installPwa);
});
</script>"""


def _esc(s: str) -> str:
    return html.escape(s)


def render_user_bar(user: dict | None, read_count: int = 0, total: int = 600) -> str:
    if user:
        pct = round(read_count / total * 100) if total else 0
        return f"""
<div class="auth-bar">
  <div class="auth-user">
    👤 <strong>{_esc(user["email"])}</strong>
    · <span class="auth-progress">{read_count}/{total} ({pct}%)</span>
  </div>
  <form method="POST" action="/logout" class="auth-links">
    <button type="submit" class="auth-link danger" style="background:none;cursor:pointer;">خروج</button>
  </form>
</div>"""
    return """
<div class="auth-bar">
  <span class="auth-user">برای ذخیره پیشرفت وارد شوید</span>
  <div class="auth-links">
    <a href="/login" class="auth-link primary">ورود</a>
    <a href="/register" class="auth-link">ثبت‌نام</a>
  </div>
</div>"""


def render_tabs(active: str, offset: int = 0, user: dict | None = None) -> str:
    parts = []
    for tab_id, fa_label, en_label, icon in TABS:
        cls = "tab active" if tab_id == active else "tab"
        q = f"?tab={tab_id}"
        if tab_id == "words" and offset:
            q += f"&offset={offset}"
        parts.append(
            f'<a href="/{q}" class="{cls}">'
            f'<span class="tab-icon">{icon}</span>'
            f'<span>{_esc(fa_label)}</span>'
            f'<span class="tab-en">{_esc(en_label)}</span>'
            f'</a>'
        )
    return f'<nav class="tabs">{"".join(parts)}</nav>'


def render_shell(active: str, content: str, offset: int = 0, extra_js: str = "", user: dict | None = None, read_count: int = 0, total: int = 600) -> str:
    auth_bar = render_user_bar(user, read_count, total)
    return f"""<!DOCTYPE html>
<html lang="fa" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="description" content="IELTS Daily Words — 4 words a day, books, and dictionaries">
<meta name="theme-color" content="#4f8cff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="IELTS Daily">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icons/icon-192.png">
<title>IELTS Daily · english.v4vendetta.sbs</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-inner">
    <div class="brand">
      <div class="brand-icon">✦</div>
      <div class="brand-text">
        <h1>IELTS Daily</h1>
        <p>english.v4vendetta.sbs · یادگیری هر روز</p>
      </div>
    </div>
    {auth_bar}
    {render_tabs(active, offset, user)}
  </div>
</div>
<div class="app-shell">
<div id="pwaBanner" class="pwa-banner">
  <div class="pwa-banner-text">📱 نصب اپ + یادآوری روزانه ساعت <strong>۱۰ صبح</strong> — کلمات امروزت رو یادت نره!</div>
  <div class="pwa-actions">
    <button type="button" id="pwaInstall" class="pwa-btn secondary">نصب اپ</button>
    <button type="button" id="pwaPush" class="pwa-btn primary">🔔 فعال‌سازی یادآوری</button>
    <button type="button" id="pwaDismiss" class="pwa-btn secondary">✕</button>
  </div>
</div>
{content}
<div class="site-footer">Made for IELTS learners · ۴ کلمه در روز</div>
</div>
{extra_js}
{PWA_JS}
</body>
</html>"""


def render_word_card(entry: dict, index: int, user: dict | None = None) -> str:
    word = entry["word"]
    word_esc = _esc(word)
    pos = _esc(entry.get("pos", ""))
    definition = _esc(entry.get("definition", ""))
    fa = entry.get("fa", "")
    fa_block = f'<p class="fa">{_esc(fa)}</p>' if fa else ""
    num = entry.get("num", 0)
    pron = entry.get("pronunciations", {})

    speak_btns = ""
    for accent, flag in (("us", "🇺🇸"), ("uk", "🇬🇧")):
        speak_btns += (
            f'<button type="button" class="speak-btn" data-word="{word_esc}" '
            f'data-accent="{accent}" data-label="{flag}" aria-label="{flag} pronunciation">'
            f'{SPEAKER_SVG}</button>'
        )

    examples = entry.get("examples", [])
    if examples and isinstance(examples[0], str):
        examples = [{"text": ex, "source": "IELTS Essential Words"} for ex in examples]
    ex_html = ""
    for ex in examples:
        ex_html += (
            f'<li><span class="ex-text">"{_esc(ex.get("text", ""))}"</span>'
            f'<span class="ex-src">— {_esc(ex.get("source", ""))}</span></li>'
        )

    src_html = ""
    for src in entry.get("sources", []):
        src_html += (
            f'<a href="{_esc(src.get("url", ""))}" target="_blank" rel="noopener" class="src-tag">'
            f'{_esc(src.get("name", ""))}</a>'
        )

    word_index = entry.get("word_index", entry.get("num", 1) - 1)
    mark_block = ""
    if user:
        mark_block = f"""
<form method="POST" action="/mark-read" class="mark-form">
  <input type="hidden" name="word_index" value="{word_index}">
  <input type="hidden" name="csrf" value="{_esc(user['csrf'])}">
  <button type="submit" class="mark-btn">✓ خواندم — دیگه نشون نده</button>
</form>"""

    return f"""
<article class="word-card" style="--i:{index}">
  <div class="word-top">
    <div class="word-left">
      <span class="word-num">#{num}</span>
      <h2 class="word-title">{word_esc}</h2>
      <p class="pos">{pos}</p>
    </div>
    <div class="speak-group">{speak_btns}</div>
  </div>
  <p class="section-label">Definition · معنی</p>
  <p class="definition">{definition}</p>
  {fa_block}
  <p class="section-label">Examples · جملات</p>
  <ul class="examples">{ex_html}</ul>
  <div class="word-sources">{src_html}</div>
  {mark_block}
</article>"""


def render_words_tab(data: dict, day: date, offset: int, fetched_label: str, user: dict | None = None) -> str:
    words = data.get("words", [])
    cards = "".join(render_word_card(w, i, user) for i, w in enumerate(words))
    day_num = data.get("day_num", 1)
    total_days = data.get("total_days", 150)
    total_words = data.get("total_words", 600)
    nums = [w.get("num", 0) for w in words]
    word_range = f"{min(nums)}–{max(nums)}" if nums else "—"
    pct = round(day_num / total_days * 100) if total_days else 0
    online = any(w.get("online") for w in words)
    live_badge = '<span class="badge live">Live · آنلاین</span>' if online else ""

    prev = f'<a href="/?tab=words&offset={offset - 1}" class="nav-btn">← دیروز</a>' if offset > 0 else ""
    next_ = f'<a href="/?tab=words&offset={offset + 1}" class="nav-btn">فردا →</a>'

    pron_map = {w["word"]: w.get("pronunciations", {}) for w in words}
    pron_json = json.dumps(pron_map).replace("</", "<\\/")

    content = f"""
<div class="page-header">
  <h2 class="page-title">{day.strftime("%A, %B %d")}</h2>
  <p class="page-sub">۴ کلمه IELTS برای امروز — با معنی، ترجمه فارسی و جمله</p>
  <div class="badges">
    <span class="badge">{day.strftime("%Y/%m/%d")}</span>
    {live_badge}
    <span class="badge">Day {day_num}/{total_days}</span>
  </div>
</div>
{cards}
<div class="footer-card">
  <div class="progress-wrap">
    <div class="progress-label"><span>Progress · پیشرفت</span><span>{pct}%</span></div>
    <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
  </div>
  <div class="meta">
    <span>Words {word_range} of {total_words}</span>
    <div class="nav-btns">{prev}{next_}</div>
  </div>
  <p class="updated">Updated · بروزرسانی: {_esc(fetched_label)}</p>
</div>"""

    js = f"""
<script>
const PRON_MAP = {pron_json};
const LANG = {{ us: "en-US", uk: "en-GB" }};
function speak(word, accent) {{
  const info = (PRON_MAP[word] || {{}})[accent] || {{}};
  if (info.audio) {{ new Audio(info.audio).play().catch(() => fallback(word, accent)); return; }}
  fallback(word, accent);
}}
function fallback(word, accent) {{
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(word);
  u.lang = LANG[accent]; u.rate = 0.88;
  const v = speechSynthesis.getVoices().find(x => x.lang === LANG[accent]);
  if (v) u.voice = v;
  speechSynthesis.speak(u);
}}
document.querySelectorAll(".speak-btn").forEach(b =>
  b.addEventListener("click", () => speak(b.dataset.word, b.dataset.accent))
);
speechSynthesis.getVoices();
</script>"""
    return render_shell("words", content, offset, js, user=user)


def render_words_tab_user(user: dict, data: dict, fetched_label: str) -> str:
    words = data.get("words", [])
    read_count = data.get("read_count", 0)
    total = data.get("total_words", 600)
    remaining = data.get("remaining", total - read_count)
    pct = round(read_count / total * 100) if total else 0

    if not words:
        content = f"""
<div class="page-header">
  <h2 class="page-title">تبریک! 🎉</h2>
  <p class="page-sub">You finished all {total} IELTS words!</p>
</div>
<div class="empty-state">
  <div class="empty-icon">🏆</div>
  <h3>همه کلمات رو خوندی!</h3>
  <p>۶۰۰ کلمه IELTS Essential Words رو کامل کردی. عالیه!</p>
</div>
<div class="footer-card">
  <div class="progress-wrap">
    <div class="progress-label"><span>Progress · پیشرفت</span><span>100%</span></div>
    <div class="progress-bar"><div class="progress-fill" style="width:100%"></div></div>
  </div>
  <p class="updated">{read_count}/{total} words completed</p>
</div>"""
        return render_shell("words", content, user=user, read_count=read_count, total=total)

    cards = "".join(render_word_card(w, i, user) for i, w in enumerate(words))
    pron_map = {w["word"]: w.get("pronunciations", {}) for w in words}
    pron_json = json.dumps(pron_map).replace("</", "<\\/")

    content = f"""
<div class="page-header">
  <h2 class="page-title">کلمات بعدی تو</h2>
  <p class="page-sub">{len(words)} کلمه unread · {remaining} کلمه باقی‌مونده</p>
  <div class="badges">
    <span class="badge live">My Progress · پیشرفت من</span>
    <span class="badge">{read_count}/{total} read</span>
  </div>
</div>
{cards}
<div class="footer-card">
  <div class="progress-wrap">
    <div class="progress-label"><span>Vocabulary Progress</span><span>{pct}%</span></div>
    <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
  </div>
  <p class="updated">Updated · بروزرسانی: {_esc(fetched_label)}</p>
</div>"""

    js = f"""
<script>
const PRON_MAP = {pron_json};
const LANG = {{ us: "en-US", uk: "en-GB" }};
function speak(word, accent) {{
  const info = (PRON_MAP[word] || {{}})[accent] || {{}};
  if (info.audio) {{ new Audio(info.audio).play().catch(() => fallback(word, accent)); return; }}
  fallback(word, accent);
}}
function fallback(word, accent) {{
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(word);
  u.lang = LANG[accent]; u.rate = 0.88;
  const v = speechSynthesis.getVoices().find(x => x.lang === LANG[accent]);
  if (v) u.voice = v;
  speechSynthesis.speak(u);
}}
document.querySelectorAll(".speak-btn").forEach(b =>
  b.addEventListener("click", () => speak(b.dataset.word, b.dataset.accent))
);
speechSynthesis.getVoices();
</script>"""
    return render_shell("words", content, user=user, read_count=read_count, total=total, extra_js=js)


def render_auth_page(title: str, subtitle: str, action: str, switch_html: str, error: str = "") -> str:
    err_block = f'<div class="form-error">{_esc(error)}</div>' if error else ""
    content = f"""
<div class="auth-card">
  <h2>{_esc(title)}</h2>
  <p class="auth-sub">{_esc(subtitle)}</p>
  {err_block}
  <form method="POST" action="{action}">
    <div class="form-group">
      <label for="email">Email · ایمیل</label>
      <input class="form-input" type="email" id="email" name="email" required autocomplete="email" placeholder="you@example.com">
    </div>
    <div class="form-group">
      <label for="password">Password · رمز عبور</label>
      <input class="form-input" type="password" id="password" name="password" required autocomplete="{'new-password' if action == '/register' else 'current-password'}" minlength="6" placeholder="حداقل ۶ کاراکتر">
    </div>
    <button type="submit" class="btn-submit">{'ورود' if action == '/login' else 'ثبت‌نام'}</button>
  </form>
  <p class="auth-switch">{switch_html}</p>
</div>"""
    return render_shell("words", content)


def render_login_page(user: dict | None, error: str = "") -> str:
    if user:
        return render_shell("words", '<script>location.href="/?tab=words"</script>')
    return render_auth_page(
        "Welcome back · ورود",
        "Sign in to track your vocabulary progress",
        "/login",
        'حساب نداری؟ <a href="/register">ثبت‌نام کن</a>',
        error,
    )


def render_register_page(user: dict | None, error: str = "") -> str:
    if user:
        return render_shell("words", '<script>location.href="/?tab=words"</script>')
    return render_auth_page(
        "Create account · ثبت‌نام",
        "Register with your email to save progress",
        "/register",
        'قبلاً ثبت‌نام کردی؟ <a href="/login">وارد شو</a>',
        error,
    )


def render_books_tab(user: dict | None = None) -> str:
    cards = ""
    for i, book in enumerate(RESOURCES["books"]):
        tags = "".join(f'<span class="rtag">{_esc(t)}</span>' for t in book.get("tags", []))
        badge_cls = "resource-badge free" if book.get("type", "").startswith("Free") else "resource-badge"
        cards += f"""
<article class="resource-card" style="--i:{i}">
  <div class="resource-icon icon-book">📚</div>
  <div class="resource-body">
    <div class="resource-top">
      <h3 class="resource-name">{_esc(book["title"])}</h3>
      <span class="{badge_cls}">{_esc(book.get("type", ""))}</span>
    </div>
    <p class="resource-author">{_esc(book.get("author", ""))}</p>
    <p class="resource-desc">{_esc(book.get("desc", ""))}</p>
    <div class="resource-tags">{tags}</div>
    <a href="{_esc(book["url"])}" target="_blank" rel="noopener" class="resource-link">
      Open / Download ↗
    </a>
  </div>
</article>"""

    content = f"""
<div class="page-header">
  <h2 class="page-title">IELTS Books · کتاب‌ها</h2>
  <p class="page-sub">بهترین منابع و کتاب‌های IELTS — رایگان و خرید</p>
</div>
<div class="resource-grid">{cards}</div>"""
    return render_shell("books", content, user=user)


def render_dictionaries_tab(user: dict | None = None) -> str:
    en_cards = ""
    for i, d in enumerate(RESOURCES["dictionaries_en_en"]):
        en_cards += f"""
<article class="resource-card" style="--i:{i}">
  <div class="resource-icon icon-dict-en">🔤</div>
  <div class="resource-body">
    <div class="resource-top">
      <h3 class="resource-name">{_esc(d["name"])}</h3>
      <span class="resource-badge">{_esc(d.get("badge", ""))}</span>
    </div>
    <p class="resource-desc">{_esc(d.get("desc", ""))}</p>
    <a href="{_esc(d["url"])}" target="_blank" rel="noopener" class="resource-link">Open Dictionary ↗</a>
  </div>
</article>"""

    fa_cards = ""
    for i, d in enumerate(RESOURCES["dictionaries_en_fa"]):
        fa_cards += f"""
<article class="resource-card" style="--i:{i + 10}">
  <div class="resource-icon icon-dict-fa">🇮🇷</div>
  <div class="resource-body">
    <div class="resource-top">
      <h3 class="resource-name">{_esc(d["name"])}</h3>
      <span class="resource-badge fa">{_esc(d.get("badge", ""))}</span>
    </div>
    <p class="resource-desc">{_esc(d.get("desc", ""))}</p>
    <a href="{_esc(d["url"])}" target="_blank" rel="noopener" class="resource-link">باز کردن ↗</a>
  </div>
</article>"""

    content = f"""
<div class="page-header">
  <h2 class="page-title">Dictionaries · دیکشنری</h2>
  <p class="page-sub">برترین دیکشنری‌های انگلیسی–انگلیسی و انگلیسی–فارسی</p>
</div>
<div class="section-divider">English → English</div>
<div class="resource-grid">{en_cards}</div>
<div class="section-divider">English → Persian · انگلیسی به فارسی</div>
<div class="resource-grid">{fa_cards}</div>"""
    return render_shell("dictionaries", content, user=user)
